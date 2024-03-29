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



@authenticated.route('/settings/', methods=['GET'])
@authenticated.route('/settings',  methods=['GET'])
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

	return make_response(render_template('settings.html', form=form, bp=bp, verified_email=email_verified)) # errmsg=session.pop('message', None))



@authenticated.route('/settings/update/', methods=['POST'])
@authenticated.route('/settings/update',  methods=['POST'])
@sc_authenticated
def api_settings_update():
	uid = session['uid']
	ba	= Account.get_by_uid(uid)
	form = SettingsForm(request.form)	#rename sf

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

	if (not update_acct):
		return make_response(jsonify(status='No changes were requested.'), 200)

	try:
		if not form.validate_on_submit():
			raise InvalidInput(errors=form.errors)

		print 'sc_api_update_settings()\tvalid submit'
		(successful, errno) = sc_update_account(uid, form.current_password.data, new_pass=update_pass, new_mail=update_mail, new_name=update_name)

		# TODO.  sc_update_account could throw errors/ return False from what?
		print("sc_api_update_settings()\tmodify acct()  = " + str(successful) + ", errno = " + str(errno))

		if not successful:
			status = SanitizedException.sanitize_message(str(errno))
			form.current_password.data = ''
			form.update_password.data = ''
			form.verify_password.data = ''
			raise SanitizedException('Update Account Failed', status, errors = {'email' : status})

		if (update_mail): ht_send_email_address_changed_confirmation(ba.email, form.email.data)		#better not throw an error
		#if (update_pass): send_passwd_change_email(ba.email)										#better not throw an error
		return make_response(jsonify(status='Saved.'), 200)

	except PasswordError as e:
		database.session.rollback()
		e.errors({ 'current_password' : e.status() })
		return e.response()
	except SanitizedException as e:
		database.session.rollback()
		return e.response()
	except AttributeError as ae:
		print 'sc_api_update_settings: AttributeError (CodeBug):', ae
		database.session.rollback()
		return make_response(ApiError('Oops. We made a mistake. Please try again later.').serialize, 500)
	except Exception as e:
		print 'sc_api_update_settings: Exception: ', e
		database.session.rollback()
		return make_response(ApiError('Oops. We made a mistake. Please try again later.').serialize, 500)

	print "sc_api_update_settings: Something went wrong - Fell Through."
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


