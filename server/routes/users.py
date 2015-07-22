################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from server.models import *
from server.routes import auth_routes as authenticated
from server.routes.helpers import *
from server.infrastructure.errors import *
from server.controllers import *



@authenticated.route('/dashboard/', methods=['GET', 'POST'])
@authenticated.route('/dashboard',  methods=['GET', 'POST'])
@sc_authenticated
def render_dashboard():
	bp = Profile.get_by_uid(session['uid'])
	message = session.pop('message', None)

	print 'render_dashboard(' + bp.prof_name + ',' + session['uid'] + ')'
	craftsperson = (session.get('role', None) == AccountRole.CRAFTSPERSON)

	try:
		projects = sc_get_projects(bp)
		for p in projects: pp(p)
	except Exception as e:
		print 'render_dashboard() tries failed -  Exception: ', type(e), e
		database.session.rollback()


	if craftsperson:
		print 'render_dashboard(), craftsperson ', craftsperson
		invite = InviteForm(request.form)
		invite.invite_userid.data = bp.account
		# get all references.
		refreqs = scdb_get_references(bp, True)
		return make_response(render_template('dashboard-professional.html', bp=bp, form=invite, craftsperson=craftsperson, br_requests=refreqs, usrmsg=message))

	return make_response(render_template('dashboard.html', bp=bp, craftsperson=craftsperson, projects=projects, usrmsg=message))



@authenticated.route('/settings/', methods=['GET', 'POST'])
@authenticated.route('/settings',  methods=['GET', 'POST'])
@sc_authenticated
def render_settings():
	""" Allows user to change his or her email settings."""
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	ba	= Account.get_by_uid(uid)

	email_verified = False if (ba.status == Account.USER_UNVERIFIED) else True
	print 'render_settings(' + str(ba.userid), bp.prof_name, ') email-verified:', email_verified

	form = SettingsForm(request.form)
	form.email.data	= ba.email
	form.name.data	= ba.name

	#nexturl = "/settings"
	#if (request.values.get('nexturl') is not None):
	nexturl = request.values.get('nexturl', '/settings')
	message = session.pop('message', None)	# was messages
	return make_response(render_template('settings.html', form=form, bp=bp, nexturl=nexturl, verified_email=email_verified, errmsg=message))



@authenticated.route('/settings/update/', methods=['POST'])
@authenticated.route('/settings/update',  methods=['POST'])
@sc_authenticated
def sc_api_update_settings():
	print "sc_api_update_settings: begin"

	uid = session['uid']
	ba	= Account.get_by_uid(uid)
	form = SettingsForm(request.form)

	# determine what needs to be updated.
	update_acct = False		# requires password.
	update_pass = None		# sends email
	update_mail = None		# sends email
	update_name = None

	if (ba.name != form.name.data):
		update_acct = True
		update_name = form.name.data

	if (ba.email != form.email.data):
		update_acct = True
		update_mail = form.email.data

	if (form.update_password.data != ""):
		update_acct = True
		update_pass = form.update_password.data

	try:
		if form.validate_on_submit():
			print 'sc_api_update_settings()\tvalid submit'

			if (update_acct == False):
				# user did not update anything.
				return jsonify(usrmsg="Cool... Nothing changed."), 200

			print 'sc_api_update_settings()\tupdate account'
			(rc, errno) = sc_update_account(uid, form.current_password.data, new_pass=update_pass, new_mail=update_mail, new_name=update_name)
			# TODO.  sc_update_account could throw errors/ return False from what?
			print("sc_api_update_settings()\tmodify acct()  = " + str(rc) + ", errno = " + str(errno))

			if (rc == False):
				errmsg = str(errno)
				errmsg = error_sanitize(errmsg)
				form.current_password.data = ''
				form.update_password.data = ''
				form.verify_password.data = ''
				return jsonify(usrmsg="Hmm... something went wrong.", errors=None), 500


			# successfully updated account
			# user changed email, password. For security, send confimration email.
			if (update_mail): ht_send_email_address_changed_confirmation(ba.email, form.email.data)		#better not throw an error
# TODO -- create send_passwd_change_email.  Need to look up Mandrill template.
			#if (update_pass): send_passwd_change_email(ba.email)										#better not throw an error
			print "sc_api_update_settings() Update should be complete"
			return jsonify(usrmsg="Settings updated"), 200
	except PasswordError as pe:
		print 'sc_api_update_settings: Password (CodeBug):', pe
		database.session.rollback()
		badpassword = {}
		badpassword['current_password'] = pe.sanitized_msg()
		return jsonify(usrmsg='We messed something up, sorry', errors=badpassword), pe.http_resp_code()
	except AttributeError as ae:
		print 'sc_api_update_settings: AttributeError (CodeBug):', ae
		database.session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500
	except Exception as e:
		print 'sc_api_update_settings: Exception: ', e
		database.session.rollback()
		return jsonify(usrmsg=e, errors=form.errors), 500

	print "sc_api_update_settings: Something went wrong - Fell Through."
	print str(form)
	return jsonify(usrmsg="Sorry, there was a problem.", errors=form.errors), 500




# rename /image/create
#@insprite_views.route('/upload', methods=['POST'])
def upload():
	log_uevent(session['uid'], " uploading file")

	bp = Profile.get_by_uid(session.get('uid'))
	orig = request.values.get('orig')
	prof = request.values.get('prof')
	update_profile_img = request.values.get('profile', False)

	print 'upload: orig', orig
	print 'upload: prof', prof

	for mydict in request.files:
		# for sec. reasons, ensure this is 'edit_profile' or know where it comes from
		print("upload()\treqfiles[" + str(mydict) + "] = " + str(request.files[mydict]))
		image_data = request.files[mydict].read()
		print ("upload()\timg_data type = " + str(type(image_data)) + " " + str(len(image_data)) )

		if (len(image_data) > 0):
			image = ht_create_image(bp, image_data, comment="")

			if (update_profile_img):
				print 'upload()\tupdate profile img'
				bp.update_profile_image(image)

	return jsonify(tmp="/uploads/" + str(image.img_id))

