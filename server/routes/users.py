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
from server.routes import sc_users
from server.routes.helpers import *
from server.infrastructure.errors import *
from server.controllers import *

# more this into controllers / tasks.
import os
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug          import secure_filename
from StringIO import StringIO
from datetime import datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@sc_users.route('/dashboard/', methods=['GET', 'POST'])
@sc_users.route('/dashboard', methods=['GET', 'POST'])
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



def render_inbox_page():
	bp = Profile.get_by_uid(session['uid'])
	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')

	try:
		messages = database.session.query(UserMessage, msg_from, msg_to)													\
							 .filter(or_(UserMessage.msg_to == bp.prof_id, UserMessage.msg_from == bp.prof_id))		\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)								\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();

		# get the list of all the comp_threads
		c_threads = filter(lambda  cmsg: (cmsg.UserMessage.msg_parent == None), messages)
		map(lambda cmsg: display_lastmsg_timestamps(cmsg, bp.prof_id, messages), c_threads)
		#for msg in c_threads: print 'MSG_Zero = ', msg.UserMessage

	except Exception as e:
		print e
		database.session.rollback()

	(inbox_threads, archived_threads) = ht_assign_msg_threads_to_mbox(bp.prof_id, c_threads)
	return make_response(render_template('inbox.html', bp=bp, inbox_threads=inbox_threads, archived_threads=archived_threads))




def render_compose_page():
	hid = request.values.get('hp')
	bp = Profile.get_by_uid(session['uid'])
	hp = None
	next = request.values.get('next')

	if (hid is not None): hp = Profile.get_by_prof_id(hid)
	return make_response(render_template('compose.html', bp=bp, hp=hp, next=next))



def get_threads():
	bp = Profile.get_by_uid(session['uid'])
	threads = []

	try:
		threads = database.session.query(UserMessage).filter(UserMessage.msg_parent == None)	\
												.filter(or_(UserMessage.msg_to == bp.prof_id, UserMessage.msg_from == bp.prof_id)).all();

		json_inbox = []
		json_archive = []
		json_messages = [msg.serialize for msg in threads]
		for msg in json_messages:
			profile_to = Profile.get_by_prof_id(msg['msg_to'])
			profile_from = Profile.get_by_prof_id(msg['msg_from'])
			msg['msg_to'] = profile_to.serialize
			msg['msg_from'] = profile_from.serialize
			if (bp == profile_to):
				mbox = json_archive if (msg['msg_flags'] & MSG_STATE_RECV_ARCHIVE) else json_inbox
			elif (bp == profile_from):
				mbox = json_archive if (msg['msg_flags'] & MSG_STATE_SEND_ARCHIVE) else json_inbox
			else:
				print 'wtf'
				continue
			mbox.append(msg)

	except Exception as e:
		print e
		database.session.rollback()

	return jsonify(inbox=json_inbox, archive=json_archive, bp=bp.prof_id)



def render_message_page():
	msg_thread_id = request.values.get('msg_thread_id')
	action = request.values.get('action')

	print 'message_thread() ', msg_thread_id, action

	if (action == None):
		#reinstate: return sc_api_get_message_thread(msg_thread_id)
		pass

	
	elif (action == "archive"):
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = database.session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
			thread_msg_zero = filter(lambda msg: (msg.msg_id == msg.msg_thread), thread_messages)[0]
			print "msg_thread id and len: ", msg_thread_id, len(thread_messages), thread_msg_zero

			if ((len(thread_messages) > 0) and (thread_msg_zero.msg_from != bp.prof_id) and (thread_msg_zero.msg_to != bp.prof_id)):
				print 'user doesn\'t have access'
				#print 'user', bp.prof_id, 'msg_from == ', thread_msg_zero.msg_from, (thread_msg_zero.msg_from != bp.prof_id)
				#print 'user', bp.prof_id, 'msg_to   == ', thread_msg_zero.msg_to  , (thread_msg_zero.msg_to   != bp.prof_id)
				thread_messages = []

			archive_flag = (thread_msg_zero.msg_to == bp.prof_id) and MSG_STATE_RECV_ARCHIVE or MSG_STATE_SEND_ARCHIVE
			updated_messages = 0
			for msg in thread_messages:
				msg.msg_flags = (msg.msg_flags | archive_flag)
				updated_messages = updated_messages + 1
				database.session.add(msg)

			if (updated_messages > 0):
				print '\"archiving\" ' + str(updated_messages) + " msgs"
				database.session.commit()

			return make_response(jsonify(usrmsg="Message thread archived.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			database.session.rollback()
		return make_response(jsonify(usrmsg="Message thread failed.", next='/inbox'), 500)
	
	elif (action == "restore"):
		print 'restoring msg_thread' + str(msg_thread_id)
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = database.session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
			thread_msg_zero = filter(lambda msg: (msg.msg_id == msg.msg_thread), thread_messages)[0]
			print "msg_thread id and len: ", msg_thread_id, len(thread_messages), thread_msg_zero

			if ((len(thread_messages) > 0) and (thread_msg_zero.msg_from != bp.prof_id) and (thread_msg_zero.msg_to != bp.prof_id)):
				print 'user doesn\'t have access'
				print 'user', bp.prof_id, 'msg_from == ', thread_msg_zero.msg_from, (thread_msg_zero.msg_from != bp.prof_id)
				print 'user', bp.prof_id, 'msg_to   == ', thread_msg_zero.msg_to  , (thread_msg_zero.msg_to   != bp.prof_id)
				thread_messages = []

			archive_flag = (thread_msg_zero.msg_to == bp.prof_id) and MSG_STATE_RECV_ARCHIVE or MSG_STATE_SEND_ARCHIVE
			updated_messages = 0

			for msg in thread_messages:
				msg.msg_flags = msg.msg_flags & ~archive_flag
				database.session.add(msg)
				updated_messages = updated_messages + 1

			if (updated_messages > 0):
				print '\"restoring\" ' + str(updated_messages) + " msgs"
				database.session.commit()

			return make_response(jsonify(usrmsg="Message thread restored.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			database.session.rollback()

		return make_response(jsonify(usrmsg="Message thread restored.", next='/inbox'), 500)	

	# find correct 400 response
	return make_response(jsonify(usrmsg="These are not the message you are looking for.", next='/inbox'), 400)






def ht_validate_profile(bp, form, form_page):
	errors = {}
	print "ht_validate_page: validating page: ", form_page

	if (form_page == "general" or form_page == "full"):
		prof_name = request.values.get("edit_name")
		prof_location = request.values.get("edit_location")
		prof_bio = request.values.get("edit_bio")

		if (len(prof_name) == 0):
			errors["edit_name"] = "Profile name is required." 
		elif (len(prof_name) > 40):
			errors["edit_name"] = "This must be less than 40 characters."

	if (form_page == "profile_photo" or form_page == "full"):

		file = request.files[form.edit_photo.name]
		print "ht_validate_page: uploaded filename is ", file.filename
		if (file):
			if allowed_file(file.filename):
				print "That photo works."
			else:
				print "File was not an image."
				errors["edit_photo"] = "Please only upload jpg, gif, or png files." 
		else :
			print "No photo uploaded."
			if (form_page == "full" and bp.prof_img == "no_pic_big.svg"):
				errors["edit_photo"] = "All mentors must upload a profile photo." 		

	if (form_page == "details" or form_page == "full"):
		prof_headline = request.values.get("edit_headline")
		# prof_url = request.values.get("edit_url")

		if (len(prof_headline) == 0):
			errors["edit_headline"] = "We'd really love for you to come up with something here." 
		elif (len(prof_headline) > 40):
			errors["edit_headline"] = "This must be less than 40 characters."

	if (form_page == "schedule" or form_page == "full"):
		# once date/time form elements are in, check if:
		# 1. specific was selected without specifying times
		# 2. day was selected without specifying time
		# 3. end time was before start time on any day

		print "ht_validate_profile: validating schedule page"

		new_avail = request.values.get("edit_availability")
		print "ht_validate_profile: new_avail: ", new_avail
		print "ht_validate_profile: edit_avail_day_tue: ", request.values.get("edit_avail_day_tue")

		if (new_avail == "2"):
			days = []
			if (request.values.get("edit_avail_day_sun") == 'y'): days.append("sun")
			if (request.values.get("edit_avail_day_mon") == 'y'): days.append("mon")
			if (request.values.get("edit_avail_day_tue") == 'y'): days.append("tue")
			if (request.values.get("edit_avail_day_wed") == 'y'): days.append("wed")
			if (request.values.get("edit_avail_day_thu") == 'y'): days.append("thu")
			if (request.values.get("edit_avail_day_fri") == 'y'): days.append("fri")
			if (request.values.get("edit_avail_day_sat") == 'y'): days.append("sat")

			print "ht_validate_profile: days: ", pp(days)

			for day in days:
				print "ht_validate_profile: day is: ", day
				start = eval("form.edit_avail_time_"+day+"_start.data")
				finish = eval("form.edit_avail_time_"+day+"_finish.data")
				
				if (start == '' or finish == ''):
					errors[day] = "Please select both a start and end time."
				else:
					try: 
						starttime = datetime.strptime(start, '%H:%M')
						finishtime = datetime.strptime(finish, '%H:%M')
						if (finishtime <= starttime):
							errors[day] = "End time must be later than start time."
					except:
						errors[day] = "Hmm... unknown error here."

			if (len(days) == 0):
				errors["edit_availability"] = "Please select the specific days and times you will be available"


	if (form_page == "payment" or form_page == "full"):
		#PROF_RATE was removed
		#prof_rate = request.values.get("edit_rate")	
		oauth_stripe = request.values.get("edit_oauth_stripe")

		#print "ht_validate_profile: prof rate is: ", prof_rate

		#try:
		#	prof_rate = int(prof_rate)
		#	if (prof_rate > 10000):
		#		errors["edit_rate"] = "Let's keep it below $10,000 for now."
		#except TypeError:
		#	errors["edit_rate"] = "Please keep it to a whole dollar amount (or zero)."

		if (oauth_stripe == ''):
			errors["edit_oauth_stripe"] = "Stripe activation is required to become a mentor."

	if (form_page == "full"):		
		tos = request.values.get("edit_mentor_tos")
		print "tos is ", tos
		if (tos != 'y'):
			errors["edit_mentor_tos"] = "You'll need to agree to the terms of service first."


	if (len(errors) == 0):
		print "ht_validate_profile: form is valid."
		valid = True
	else:
		print "ht_validate_profile: errors: ", pp(errors)
		valid = False
	return valid, errors



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ht_update_profile(ba, bp, form, form_page):
	print 'ht_update_profile:', bp.prof_id
	print 'ht_update_profile: form_page: ', form_page
	if (form_page == "full"):
		print 'ht_update_profile: save all elements'
	else:
		print 'ht_update_profile: save only elements from page: ', form_page
	for key in request.values:
		print '\t', key, request.values.get(key)
	update = False
	
	if (form_page == 'general' or form_page == 'full'):
		bp.prof_name = form.edit_name.data
		bp.location = form.edit_location.data 			
		bp.prof_bio  = form.edit_bio.data
		return True

	if (form_page == 'details' or form_page == 'full'):	
		bp.headline = form.edit_headline.data 			
		bp.prof_url  = form.edit_url.data
		return True

	# check for photo, name should be PHOTO_HASH.VER[#].SIZE[SMLX]
	if (form_page == 'profile_photo' or form_page == 'full'):
		file = request.files[form.edit_photo.name]
		print "ht_validate_page: uploaded filename is ", file.filename
		if (file and allowed_file(file.filename)):
			image_data = file.read()
			print "api_update_profile: image was uploaded"
			destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			trace (destination_filename + ", sz = " + str(len(image_data)))

			print 'api_update_profile: s3'
			conn = boto.connect_s3(sc_server.config["S3_KEY"], sc_server.config["S3_SECRET"]) 
			b = conn.get_bucket(sc_server.config["S3_BUCKET"])
			sml = b.new_key(sc_server.config["S3_DIRECTORY"] + destination_filename)
			sml.set_contents_from_file(StringIO(image_data))
			imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
			bp.prof_img = destination_filename

		# if URL is set, ensure 'http(s)://' is part of it
		if (bp.prof_url):
			if (bp.prof_url[:8] != "https://"):
				if (bp.prof_url[:7] != "http://"):
					bp.prof_url = "http://" + bp.prof_url;
		return True


#@insprite_views.route('/profile/upgrade', methods=['GET', 'POST'])
#@req_authentication
def upgrade_profile():
	return redirect('/profile/edit#mentor')



#@req_authentication
#@insprite_views.route("/upload_portfolio", methods=['GET', 'POST'])
def render_multiupload_page():
	bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('upload_portfolio.html', bp=bp))


	

#@req_authentication
#@insprite_views.route("/edit_portfolio", methods=['GET', 'POST'])
def render_edit_portfolio_page():
	bp = Profile.get_by_uid(session['uid'])

	print "render_edit_portfolio_page(): get all images for profile:"
	portfolio = database.session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))




#@insprite_views.route("/review/new/<review_id>", methods=['GET', 'POST'])
#@req_authentication
def render_review_meeting_page(review_id):
	"""renders review page.  Results posted to ht_api_review"""
	print 'render_review_meeting()\treview_id =', review_id
	# if review already exists, return a kind message.

	try:
		review = Review.get_by_id(review_id)
		review_days_left = review.time_until_review_disabled()
		if (review_days_left < 0):
			return jsonify(msg='Reviews are only available for 30 days after a meeting'), 400
		if (review.completed()):
			raise StateTransitionError(review.review_id, review.rev_status, review.rev_status, msg="Reviews cannot be modified once submitted")
			#return make_response(jsonify(msg='Reviews cannot be modified once submitted'), 400

		bp = Profile.get_by_uid(session['uid'])
		ba = Account.get_by_uid(bp.account)

		author = bp
		review.validate_author(author.prof_id)

		reviewed = Profile.get_by_prof_id(review.prof_reviewed)
		print 'render_review()\t, author =', author.prof_id, author.prof_name, ba.email
		print 'render_review()\t, review author =', review.prof_authored
		print 'render_review()\t, review revied =', review.prof_reviewed

		review_form = ReviewForm(request.form)
		review_form.review_id.data = str(review_id)
		return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=reviewed, form=review_form))

	except SanitizedException as se:
		print se
		database.session.rollback()
		return jsonify(usrmsg=se.sanitized_msg())
	except Exception as e:
		print type(e), e
		database.session.rollback()
		raise e
	except IndexError as ie:
		print 'trying to access, review, author or reviewer account and failed'
		database.session.rollback()
		raise ie




@sc_users.route('/settings', methods=['GET', 'POST'])
@req_authentication
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



@sc_users.route('/settings/update', methods=['POST'])
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
#@dbg_enterexit
#@req_authentication
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



@sc_users.route('/project/edit', methods=['GET', 'POST'])
@sc_users.route('/project/edit/<string:pid>', methods=['GET', 'POST'])
@req_authentication
def render_edit_project(pid=None):
	bp = Profile.get_by_uid(session['uid'])
	print "render_edit_project: profile[" + str(bp.prof_id) + "] project[" + str(pid) + "]"

	form = ProjectForm(request.form)
	project = Project.get_by_proj_id(pid, bp) # FEATURE: project should be _owned_ by bp (not checked right now)
	if (project):
		form.proj_id.data	= project.proj_id
		form.proj_name.data	= project.proj_name
		form.proj_addr.data = project.proj_addr
		form.proj_desc.data = project.proj_desc
		form.proj_max.data	= project.proj_max
		form.proj_timeline.data	= project.timeline
		form.proj_contact.data	= project.contact

#		print "render_edit_project: checking for scheduled time."
#		schedule_call = Availability.get_project_scheduled_time(project.proj_id)
#		if (schedule_call is not None):
#				print "render_edit_project: setting values to ", str(schedule_call.avail_weekday), str(schedule_call.avail_start), str(schedule_call.avail_start)[:-3]
#				form.avail_day.data  = schedule_call.avail_weekday
#				form.avail_time.data = str(schedule_call.avail_start)[:-3]
	else:
		# set proj_id to 'new'
		form.proj_id.data	= 'new'

	return make_response(render_template('edit_project.html', form=form, bp=bp))




@sc_users.route('/project/schedule/<mode>/<string:pid>', methods=['GET', 'POST'])
@req_authentication
def api_project_schedule_consultation(mode, pid=None):
	bp = Profile.get_by_uid(session['uid'])
	try:
		project = Project.get_by_proj_id(pid, bp)
		if (project):
			session['message'] = 'A project specialist will contact you by ' + str(mode) + ' within 24 hours.'
	except Exception as e:
		print e
	return redirect('/dashboard')





@sc_users.route('/project/update', methods=['POST'])
@req_authentication
def api_update_project(usrmsg=None):
	# Process the edit profile form
	print "api_proj_update: start"

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	
	# validate all data manually. 
	form = ProjectForm(request.form)

	try:
		errors = "CAH, no errors"
		if form.validate_on_submit():
			print "api_proj_update: valid submit"

			if (True):
				project = None
				newproj = False
				print "api_proj_update: id = ", form.proj_id.data
				if form.proj_id is not 'new':
					# find project.
					project = Project.get_by_proj_id(form.proj_id.data)

				if (project == None):
					print "api_proj_update: create new project"
					project = Project(form.proj_name.data, uid)
					newproj = True;
					if (project == None):
						err_msg = 'Error: user(%s) gave us a bad ID(%s), BAIL!' % (uid, form.proj_name.data)
						raise err_msg

				print "api_proj_update: set details"
				project.proj_name	= form.proj_name.data
				project.proj_addr	= form.proj_addr.data
				project.proj_desc	= form.proj_desc.data
				project.proj_min	= 0	#hardcoding to zero
				project.proj_max	= form.proj_max.data	#rename_budget (budget_actual?)
				project.timeline 	= form.proj_timeline.data
				project.contact		= form.proj_contact.data
				project.updated		= datetime.utcnow()

				print "api_proj_update: add"
				database.session.add(project)
				database.session.commit()
				if (newproj): sc_email_newproject_created(bp, project)
				return jsonify(usrmsg="project updated", proj_id=project.proj_id), 200
			else:
				database.session.rollback()
				print "api_proj_update: update error"
				return jsonify(usrmsg="We messed something up, sorry", errors=form.errors), 500
		else:
			print 'api_proj_update: invalid POST', form.errors

		print "api_proj_update: invalid", 
		return jsonify(usrmsg='Sorry, some required info was missing or in an invalid format. Please check the form.', errors=form.errors), 500

	except AttributeError as ae:
		print "api_proj_update: exception", ae
		database.session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500
	except Exception as e:
		print type(e), e
		print "api_proj_update: exception", e
		database.session.rollback()
		return jsonify(usrmsg=e), 500

	print "api_update_profile: Something went wrong - Fell Through."
	print "here is the form object:"
	print str(form)

	print "api_proj_update: return"
	return jsonify(usrmsg="Something went wrong."), 500






#HELPER FUNCTIONS.

#@insprite_views.route('/uploads/<filename>')
#def uploaded_file(filename):
	# add sec protection?
#	return send_from_directory(sc_server.config['SC_UPLOAD_DIR'], filename)



def ht_create_image(profile, image_data, comment=None):
	print 'upload()\tht_create_image()\tenter'
	imgid = secure_filename(hashlib.sha1(image_data).hexdigest()) + '.jpg'
	image = Image.get_by_id(imgid)
	if (image is None):
		print 'upload()\tht_image_create\t image does not exist.  Create it.'
		# image doesn't exist. Create and upload to S3
		image = Image(imgid, profile.prof_id, comment)
		try:
			ht_upload_image_to_S3(image, image_data)
			database.session.add(image)
			database.session.commit()
		except IntegrityError as ie:
			# image already exists.
			print 'upload()\tht_image_create() funny seeing image already exist here.'
			print 'upload: exception', type(e), e
			database.session.rollback()
		except Exception as e:
			print 'upload: exception', type(e), e
			database.session.rollback()
	return image



def ht_upload_image_to_S3(image, image_data):
	f = open(os.path.join(sc_server.config['SC_UPLOAD_DIR'], image.img_id), 'w')
	f.write(image_data)
	f.close()

	print 'upload()\tupload_image_to_S3\tpush image to S3.'
	s3_con = boto.connect_s3(sc_server.config["S3_KEY"], sc_server.config["S3_SECRET"])
	s3_bkt = s3_con.get_bucket(sc_server.config["S3_BUCKET"])
	s3_key = s3_bkt.new_key(sc_server.config["S3_DIRECTORY"] + image.img_id)
	print 'upload()\tupload_image_to_S3\tcreated s3_key.'
	s3_key.set_contents_from_file(StringIO(image_data))





def display_lastmsg_timestamps(msg, prof_id, all_messages):
	#print 'For Thread ', msg.UserMessage.msg_thread, msg.UserMessage.msg_subject[:20]
	thread_msgs = filter(lambda cmsg: (cmsg.UserMessage.msg_thread == msg.UserMessage.msg_thread), all_messages)
	thread_msgs.sort(key=lambda cmsg: (cmsg.UserMessage.msg_created))
	#for msg in thread_msgs:
	#	ts_open = msg.UserMessage.msg_opened.strftime('%b %d %I:%M:%S') if msg.UserMessage.msg_opened is not None else str('Unopened')
	#	print '\t Sorted [%s|%s] %r' % (msg.UserMessage.msg_thread, msg.UserMessage.msg_parent, ts_open)
	setattr(msg, 'lastmsg', thread_msgs[-1].UserMessage)
	#setattr(msg, 'lastmsg_sent', thread_msgs[-1].UserMessage.msg_created)
	#setattr(msg, 'lastmsg_open', thread_msgs[-1].UserMessage.msg_opened)
	#setattr(msg, 'lastmsg_to',   thread_msgs[-1].msg_to)



def error_sanitize(message):
	if (message[0:16] == "(IntegrityError)"):
		message = "Email already in use."
	return message
