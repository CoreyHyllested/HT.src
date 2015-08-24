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



<<<<<<< HEAD

@sc_users.route('/dashboard/', methods=['GET', 'POST'])
@sc_users.route('/dashboard', methods=['GET', 'POST'])
=======
@authenticated.route('/dashboard/', methods=['GET', 'POST'])
@authenticated.route('/dashboard',  methods=['GET', 'POST'])
>>>>>>> master
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


<<<<<<< HEAD
@sc_users.route('/referral/create', methods=['GET', 'POST'])
@sc_authenticated
def render_referral_create():
	bp = Profile.get_by_uid(session['uid'])
	ba = Account.get_by_uid(session['uid'])
	invite = InviteForm(request.form)
	return make_response(render_template('referral-create.html', bp=bp, form=invite))




#@testing.route("/purchase_me", methods=['GET', 'POST'])
#@sc_authenticated
def render_purchase_page():
	bp = Profile.get_by_uid(session['uid'])
	gift = GiftForm(request.form)
	return make_response(render_template('purchase.html', bp=bp, form=gift, STRIPE_PK=ht_server.config['STRIPE_PUBLIC']))



#@insprite_views.route("/inbox", methods=['GET', 'POST'])
#@req_authentication
def render_inbox_page():
	bp = Profile.get_by_uid(session['uid'])
	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')

	try:
		messages = db_session.query(UserMessage, msg_from, msg_to)													\
							 .filter(or_(UserMessage.msg_to == bp.prof_id, UserMessage.msg_from == bp.prof_id))		\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)								\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();

		# get the list of all the comp_threads
		c_threads = filter(lambda  cmsg: (cmsg.UserMessage.msg_parent == None), messages)
		map(lambda cmsg: display_lastmsg_timestamps(cmsg, bp.prof_id, messages), c_threads)
		#for msg in c_threads: print 'MSG_Zero = ', msg.UserMessage

	except Exception as e:
		print e
		db_session.rollback()

	(inbox_threads, archived_threads) = ht_assign_msg_threads_to_mbox(bp.prof_id, c_threads)
	return make_response(render_template('inbox.html', bp=bp, inbox_threads=inbox_threads, archived_threads=archived_threads))




#@req_authentication
#@insprite_views.route("/compose", methods=['GET', 'POST'])
def render_compose_page():
	hid = request.values.get('hp')
	bp = Profile.get_by_uid(session['uid'])
	hp = None
	next = request.values.get('next')

	if (hid is not None): hp = Profile.get_by_prof_id(hid)
	return make_response(render_template('compose.html', bp=bp, hp=hp, next=next))




#@req_authentication
#@insprite_views.route("/get_threads", methods=['GET', 'POST'])
def get_threads():
	bp = Profile.get_by_uid(session['uid'])
	threads = []

	try:
		threads = db_session.query(UserMessage).filter(UserMessage.msg_parent == None)	\
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
		db_session.rollback()

	return jsonify(inbox=json_inbox, archive=json_archive, bp=bp.prof_id)




#@req_authentication
#@insprite_views.route("/message", methods=['GET', 'POST'])
def render_message_page():
	msg_thread_id = request.values.get('msg_thread_id')
	action = request.values.get('action')

	print 'message_thread() ', msg_thread_id, action

	if (action == None):
		return ht_api_get_message_thread(msg_thread_id)
	
	elif (action == "archive"):
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = db_session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
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
				db_session.add(msg)

			if (updated_messages > 0):
				print '\"archiving\" ' + str(updated_messages) + " msgs"
				db_session.commit()

			return make_response(jsonify(usrmsg="Message thread archived.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			db_session.rollback()
		return make_response(jsonify(usrmsg="Message thread failed.", next='/inbox'), 500)
	
	elif (action == "restore"):
		print 'restoring msg_thread' + str(msg_thread_id)
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = db_session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
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
				db_session.add(msg)
				updated_messages = updated_messages + 1

			if (updated_messages > 0):
				print '\"restoring\" ' + str(updated_messages) + " msgs"
				db_session.commit()

			return make_response(jsonify(usrmsg="Message thread restored.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			db_session.rollback()

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
			if (request.values.get("edit_avail_day_sun") == 'y'):
				days.append("sun")
			if (request.values.get("edit_avail_day_mon") == 'y'):
				days.append("mon")
			if (request.values.get("edit_avail_day_tue") == 'y'):
				days.append("tue")
			if (request.values.get("edit_avail_day_wed") == 'y'):
				days.append("wed")
			if (request.values.get("edit_avail_day_thu") == 'y'):
				days.append("thu")
			if (request.values.get("edit_avail_day_fri") == 'y'):
				days.append("fri")
			if (request.values.get("edit_avail_day_sat") == 'y'):
				days.append("sat")

			print "ht_validate_profile: days: ", pprint(days)	

			for day in days:
				print "ht_validate_profile: day is: ", day
				start = eval("form.edit_avail_time_"+day+"_start.data")
				finish = eval("form.edit_avail_time_"+day+"_finish.data")
				
				# print "start is", start
				# print "finish is", finish

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
		print "ht_validate_profile: errors: ", pprint(errors)
		valid = False
	return valid, errors



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ht_update_avail_timeslots(bp, form):
	print "ht_update_avail_timeslots: begin"
	update = False
	d = {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}

	# First delete the existing entries in the Availability table for this profile.
	avail = Availability.get_by_prof_id(bp.prof_id)
	for o in avail:
		print "ht_update_avail_timeslots: deleting a slot."
		db_session.delete(o)

	if (bp.availability == 1): # They chose flexible scheduling. All we do is delete any existing timeslots.
		print "ht_update_avail_timeslots: availability is flexible - remove existing timeslots."
		db_session.commit()
		return True
	elif (bp.availability == 2): # They chose timeslot scheduling - need to parse and insert.
		print "ht_update_avail_timeslots: availability is specific - extract preferences."

		# Now we go through the submitted form and see what was chosen. We will need to do a separate db add for each time slot.
		
		days = []

		if (request.values.get("edit_avail_day_sun") == 'y'):
			days.append("sun")
		if (request.values.get("edit_avail_day_mon") == 'y'):
			days.append("mon")
		if (request.values.get("edit_avail_day_tue") == 'y'):
			days.append("tue")
		if (request.values.get("edit_avail_day_wed") == 'y'):
			days.append("wed")
		if (request.values.get("edit_avail_day_thu") == 'y'):
			days.append("thu")
		if (request.values.get("edit_avail_day_fri") == 'y'):
			days.append("fri")
		if (request.values.get("edit_avail_day_sat") == 'y'):
			days.append("sat")

		print "ht_update_avail_timeslots: avail days: ", days
		for day in days:
			# generate the variable name string, and extract its value using eval
			start = eval("form.edit_avail_time_"+day+"_start.data")
			finish = eval("form.edit_avail_time_"+day+"_finish.data")
			print "-"*24
			print "ht_update_avail_timeslots: adding slot on", day

			try:
				# Initialize the avail timeslot
				print "ht_update_avail_timeslots: initializing timeslot"
				newavail = ht_create_avail_timeslot(bp)
				if (newavail):
					print "ht_update_avail_timeslots: initializing timeslot successful"
					
					# Add the new fields
					for k, v in d.iteritems():
						if v == day:
							thisday = v
							newavail.avail_weekday = k

					newavail.avail_start = start
					newavail.avail_finish = finish

					print "ht_update_avail_timeslots: db add for new timeslot:", newavail.avail_weekday, "(", thisday, ") -", newavail.avail_start, "=>", newavail.avail_finish
					db_session.add(newavail)
					update = True
				else:
					print "ht_update_avail_timeslots: initializing timeslot FAILED"
			except:
				print "ht_update_avail_timeslots: Error - something went wrong."
				update = False

		if (update == True):	
			print "ht_update_avail_timeslots: commit"	
			db_session.commit()
			return True
		else:
			print "ht_update_avail_timeslots: fail"	
			db_session.rollback()
			return False
	else:
		print "ht_update_avail: Availability wasn't set - something screwed up."
		db_session.rollback()
		return False

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
		# bp.industry = Industry.industries[int(form.edit_industry.data)]
		bp.headline = form.edit_headline.data 			
		bp.prof_url  = form.edit_url.data
		return True

#PROF_RATE was removed
#	if (form_page == 'payment' or form_page == 'full'):	
#		bp.prof_rate = form.edit_rate.data		
#		ba.stripe_cust = form.edit_oauth_stripe.data
#		return True

	if (form_page == 'schedule' or form_page == 'full'):

		bp.availability = form.edit_availability.data

		# Send to ht_update_avail_timeslots to update the user's availability, and their time slots in the Availability table.
		avail_update = ht_update_avail_timeslots(bp, form)
		if (avail_update):
			print 'ht_update_profile: avail timeslot update successful.'
		else:
			print 'ht_update_profile: avail update failed.'

		return True

	if (form_page == 'mentor'):
		if (bp.availability == 0):
			bp.availability = 1
			return True
		else:
			print "Already a mentor. Moving on..."
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

			#print source_extension
			print 'api_update_profile: s3'
			conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
			b = conn.get_bucket(ht_server.config["S3_BUCKET"])
			sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
			sml.set_contents_from_file(StringIO(image_data))
			imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
			bp.prof_img = destination_filename

		# if URL is set, ensure 'http(s)://' is part of it
		if (bp.prof_url):
			if (bp.prof_url[:8] != "https://"):
				if (bp.prof_url[:7] != "http://"):
					bp.prof_url = "http://" + bp.prof_url;

		return True

	#TODO: re-enable this; fails on commit (can't compare offset-naive and offset-aware datetimes)
	# bp.updated  = dt.utcnow()


#@insprite_views.route('/profile/upgrade', methods=['GET', 'POST'])
#@req_authentication
def upgrade_profile():
	uid = session['uid']
	bp = Profile.get_by_uid(uid)

	if (bp.availability > 0):
		print "upgrade_profile(): Whahappen? User is already a mentor!"

	# return make_response(render_edit_profile(activate="true"))
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
	portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))




#@insprite_views.route('/schedule/getdays', methods=['GET'])
#@req_authentication
def get_schedule_days():
	print "get_schedule_days: start"
	mentor_id = request.values.get('mentor_id')
	availdays = []
	print "get_schedule_days: mentor_id:", mentor_id
	avail = Availability.get_by_prof_id(mentor_id)

	try:
		availdays = Availability.get_avail_days(mentor_id)
		if (len(availdays) > 0):
			print "get_schedule_days: user available on days ", str(availdays)
		else:
			print "get_schedule_days: user availability not found"

	except Exception as e:
		print "get_schedule_days: exception:", e
		print "get_schedule_days: Couldn't find availability for that user."

	return jsonify(availdays=availdays), 200	


#@insprite_views.route('/schedule/gettimes', methods=['GET'])
#@req_authentication
def get_schedule_times():
	print "get_schedule_times: start"
	day = request.values.get('day')
	mentor_id = request.values.get('mentor_id')
	print "get_schedule_times: day:", day
	print "get_schedule_times: mentor_id:", mentor_id
	avail = Availability.get_by_prof_id(mentor_id)

	try:
		start, finish = Availability.get_avail_by_day(mentor_id, day)
		print "get_schedule_times: start:", start
		print "get_schedule_times: finish:", finish

		return jsonify(start=str(start), finish=str(finish)), 200

	except Exception as e:
		print "get_schedule_times: exception:", e
		print "get_schedule_times: Couldn't find availability for that day."



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
		db_session.rollback()
		return jsonify(usrmsg=se.sanitized_msg())
	except Exception as e:
		print type(e), e
		db_session.rollback()
		raise e
	except IndexError as ie:
		print 'trying to access, review, author or reviewer account and failed'
		db_session.rollback()
		raise ie




@sc_users.route('/settings', methods=['GET', 'POST'])
@req_authentication
=======

@authenticated.route('/settings/', methods=['GET'])
@authenticated.route('/settings',  methods=['GET'])
@sc_authenticated
>>>>>>> master
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


