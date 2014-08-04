################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
# All Rights Reserved.
#
# All information contained is the property of Insprite, LLC.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Insprite, LLC.
#################################################################################


from server.ht_utils import *
from server.infrastructure.srvc_database import db_session
from server.models import *
from server.infrastructure.errors import *
from server.controllers import *
from . import insprite_views
from .api import ht_api_get_message_thread
from .helpers import *
from ..forms import ProfileForm, SettingsForm, NTSForm, ReviewForm, LessonForm

# more this into controllers / tasks.
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug          import secure_filename
from StringIO import StringIO
from pprint import pprint


@insprite_views.route('/home',      methods=['GET', 'POST'])
@insprite_views.route('/dashboard', methods=['GET', 'POST'])
@req_authentication
def render_dashboard(usrmsg=None):
	""" Provides Hero their personalized homepage.
		- Show calendar with all upcoming appointments
		- Show any statistics.
	"""

	bp = Profile.get_by_uid(session['uid'])
	insprite_msg = session.pop('messages', None)
	print 'render_dashboard(' + bp.prof_name + ',' + session['uid'] + ')'

	unread_msgs = []

	try:
		(props, appts, rview) = ht_get_active_meetings(bp)
		active_reviews = ht_get_active_author_reviews(bp)
		active_lessons = ht_get_active_lessons(bp)
		unread_msgs = ht_get_unread_messages(bp)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	
	if (usrmsg is None and insprite_msg):
		usrmsg = insprite_msg
		print 'render_dashboard() usrmsg = ', usrmsg

	map(lambda msg: display_partner_message(msg, bp.prof_id), unread_msgs)
	return make_response(render_template('dashboard.html', title="- " + bp.prof_name, bp=bp, lessons=active_lessons, proposals=props, appointments=appts, messages=unread_msgs, reviews=active_reviews, errmsg=usrmsg))




@insprite_views.route("/inbox", methods=['GET', 'POST'])
@req_authentication
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




@req_authentication
@insprite_views.route("/compose", methods=['GET', 'POST'])
def render_compose_page():
	hid = request.values.get('hp')
	bp = Profile.get_by_uid(session['uid'])
	hp = None
	next = request.values.get('next')

	if (hid is not None): hp = Profile.get_by_prof_id(hid)
	return make_response(render_template('compose.html', bp=bp, hp=hp, next=next))




@req_authentication
@insprite_views.route("/get_threads", methods=['GET', 'POST'])
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




@req_authentication
@insprite_views.route("/message", methods=['GET', 'POST'])
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




@insprite_views.route('/edit', methods=['GET', 'POST'])
@req_authentication
def render_edit():
	""" Provides Hero space to update their information.  """

	uid = session['uid']
	bp	= Profile.get_by_uid(uid)

	form = ProfileForm(request.form)
	if form.validate_on_submit():
		try:
			print ("form is valid")
			bp.prof_rate = form.edit_rate.data
			bp.headline = form.edit_headline.data 
			bp.location = form.edit_location.data 
			bp.industry = Industry.industries[int(form.edit_industry.data)] 
			bp.prof_name = form.edit_name.data
			bp.prof_bio  = form.edit_bio.data
			bp.prof_url  = form.edit_url.data

			#TODO: re-enable this; fails on commit (can't compare offset-naive and offset-aware datetimes)
			# bp.updated  = dt.utcnow()

			# check for photo, name should be PHOTO_HASH.VER[#].SIZE[SMLX]
			image_data = request.files[form.edit_photo.name].read()
			if (len(image_data) > 0):
				destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
				trace (destination_filename + ", sz = " + str(len(image_data)))

				#print source_extension
				print 's3'
				conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
				b = conn.get_bucket(ht_server.config["S3_BUCKET"])
				sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
				sml.set_contents_from_file(StringIO(image_data))
				imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
				bp.prof_img = destination_filename

			# ensure 'http(s)://' exists
			if (bp.prof_url[:8] != "https://"):
				if (bp.prof_url[:7] != "http://"):
					bp.prof_url = "http://" + bp.prof_url;

			print 'add'
			db_session.add(bp)
			print 'commit'
			db_session.commit()
			log_uevent(uid, "update profile")

			return jsonify(usrmsg="profile updated"), 200

		except AttributeError as ae:
			print 'hrm. must have changed an object somehwere'
			print ae
			db_session.rollback()
			return jsonify(usrmsg='We messed something up, sorry'), 500

		except Exception as e:
			print e
			db_session.rollback()
			return jsonify(usrmsg=e), 500

	elif request.method == 'POST':
		log_uevent(uid, "editform isnt' valid" + str(form.errors))
		print 'shoulding this fire?'
		return jsonify(usrmsg='Invalid Request: ' + str(form.errors)), 500

	x = 0
	for x in range(len(Industry.industries)):
		if Industry.industries[x] == bp.industry:
			form.edit_industry.data = str(x)
			break

	form = ProfileForm(request.form)
	form.edit_name.data     = bp.prof_name
	form.edit_rate.data     = bp.prof_rate
	form.edit_headline.data = bp.headline
	form.edit_location.data = bp.location
	form.edit_industry.data = str(x)
	form.edit_url.data      = bp.prof_url #replace.httpX://www.
	form.edit_bio.data      = bp.prof_bio
	photoURL 				= 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(bp.prof_img)
	return make_response(render_template('edit.html', form=form, bp=bp, photoURL=photoURL))




@req_authentication
@insprite_views.route("/upload_portfolio", methods=['GET', 'POST'])
def render_multiupload_page():
	bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('upload_portfolio.html', bp=bp))


	

@req_authentication
@insprite_views.route("/edit_portfolio", methods=['GET', 'POST'])
def render_edit_portfolio_page():
	bp = Profile.get_by_uid(session['uid'])
	lesson_id = request.values.get('lesson_id', False)

	if (lesson_id):
		print "render_edit_portfolio_page(): Lesson ID:", lesson_id
		# warning.  dangerous. returning a LessonMap (which has same fields)
		portfolio = ht_get_serialized_images_for_lesson(lesson_id)
	else:
		print "render_edit_portfolio_page(): get all images for profile:"
		portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))




@insprite_views.route('/teacher/signup', methods=['GET', 'POST'])
@req_authentication
def render_teacher_signup_page(usrmsg = None):
	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	pi = Oauth.get_stripe_by_uid(uid)
	title = '- Sign Up to Teach'
	edit  = None

	# StripeConnect req'd for payments
	stripe = 'No Stripe Account Found.'
	if (pi is not None): stripe = pi.oa_account
	session['next_url']='/teacher/signup#payment'

	if (bp.availability > 0):
		print "render_teacher_signup_page(): User is already a teacher! Repopulate the page ..."
		title = '- Edit Your Info'
		edit  = True
	return make_response(render_template('teacher_signup.html', title='- Sign Up to Teach', bp=bp, oa_stripe=stripe, edit=edit))




@insprite_views.route('/teacher/activate', methods=['GET', 'POST'])
@req_authentication
def activate_seller():
	""" A regular user is signing up to be a seller.  """

	print "-"*32
	print 'activate_seller(): begin'
	uid = session['uid']
	bp = Profile.get_by_uid(session.get('uid'))
	ba = Account.get_by_uid(session.get('uid'))
	form = request.form

	# TODO - put this back in
	# if form.validate_on_submit():

	try:
		bp.availability = form.get('ssAvailOption')
		bp.stripe_cust = form.get('oauth_stripe')

		print "activate_seller(): availability:", bp.availability
		print "activate_seller(): stripe_cust:", bp.stripe_cust

		# Not used yet:
		# bp.avail_times = int(form.ssAvailTimes.data)

		# TODO: re-enable this; fails on commit (can't compare offset-naive and offset-aware datetimes)
		# bp.updated  = dt.utcnow()

		# check for photo - if seller is uploading new one, we replace their old prof_img with it.
		# TODO: what happens if someone wants to just keep their old one?

		this_image = request.files['ssProfileImage']
		this_image_data = this_image.read()

		print "activate_seller(): this_image:", str(this_image)
		print "activate_seller(): this_image_data Len:", len(this_image_data)
		
		if (len(this_image_data) > 0):
			destination_filename = str(hashlib.sha1(this_image_data).hexdigest()) + '.jpg'
			trace (destination_filename + ", sz = " + str(len(this_image_data)))
			print 'activate_seller(): s3'
			conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"])
			b = conn.get_bucket(ht_server.config["S3_BUCKET"])
			sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
			sml.set_contents_from_file(StringIO(this_image_data))
			bp.prof_img = destination_filename

		print 'activate_seller(): add'
		db_session.add(bp)
		print 'activate_seller(): commit'
		db_session.commit()
		log_uevent(uid, "activate seller profile")
		print 'activate_seller(): SUCCESS! Seller activated.'
		
		# TODO - add something back in to tell page the status
		# return redirect("/lesson/add")


		return make_response(initialize_lesson("first"))

	except AttributeError as ae:
		print 'activate_seller(): hrm. must have changed an object somewhere:', ae
		db_session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500

	except Exception as e:
		print 'activate_seller(): Exception:', e
		db_session.rollback()
		return jsonify(usrmsg="Something else screwed up."), 500


# This route initiates a new lesson
@insprite_views.route('/lesson/new', methods=['GET', 'POST'])
@req_authentication
def initialize_lesson(version=None):
	bp = Profile.get_by_uid(session['uid'])
	
	if (bp.availability == 0): return redirect('/dashboard')

	print 'initialize_lesson: Initializing Lesson...'
	print 'initialize_lesson: Version is ', version
	lesson = ht_create_lesson(bp)
	if (lesson is None): return make_response(jsonify(usrmsg='Something bad'), 500)
	lesson_id = lesson.lesson_id

	form = LessonForm(request.form)

	if (version == "first"):
		return redirect('/lesson/new/'+lesson_id +'?version=first')
	else:
		return redirect('/lesson/new/'+lesson_id)


# The new lesson has been initialized - redirect to the form
@insprite_views.route('/lesson/new/<lesson_id>', methods=['GET', 'POST'])
@req_authentication
def render_new_lesson(lesson_id, form=None, errmsg=None):
	bp = Profile.get_by_uid(session['uid'])
	version = request.values.get("version")
	if (bp.availability == 0): return redirect('/dashboard')
	
	print "render_new_lesson: lesson_id is", lesson_id

	lesson = Lesson.get_by_id(lesson_id)

	# Form will be none unless we are here after an unsuccessful form validation.
	if (form == None):
		print "render_edit_lesson: no form submitted"
		
		# In case the user went back in their browser to this page, after submitting
		form = LessonForm(request.form)
		form.lessonTitle.data = lesson.lesson_title
		form.lessonDescription.data = lesson.lesson_description
		form.lessonAddress1.data = lesson.lesson_address_1
		form.lessonAddress2.data = lesson.lesson_address_2
		form.lessonCity.data = lesson.lesson_city
		form.lessonState.data = lesson.lesson_state
		form.lessonZip.data = lesson.lesson_zip
		form.lessonCountry.data = lesson.lesson_country
		form.lessonAddressDetails.data = lesson.lesson_address_details
		form.lessonRate.data = lesson.lesson_rate
		form.lessonRateUnit.data = lesson.lesson_rate_unit
		form.lessonPlace.data = lesson.lesson_loc_option
		form.lessonIndustry.data = lesson.lesson_industry
		form.lessonDuration.data = lesson.lesson_duration
		form.lessonAvail.data = lesson.lesson_avail
		form.lessonMakeLive.data = 'y'

		if (form.lessonRate.data <= 0):
			form.lessonRate.data = bp.prof_rate		

		if (lesson.lesson_flags == 2):
			form.lessonMakeLive.data = None

	else:
		# Submitted form didn't validate - repopulate from the submitted form instead of from the database.
		print "render_edit_lesson: invalid form imported"
		

	return make_response(render_template('add_lesson.html', bp=bp, form=form, lesson_id=lesson_id, errmsg=errmsg, version=version))



# User is choosing to edit a lesson they previously saved - display the form
@insprite_views.route('/lesson/edit/<lesson_id>', methods=['GET', 'POST'])
@req_authentication
def render_edit_lesson(lesson_id, form=None, errmsg=None):
	bp = Profile.get_by_uid(session['uid'])
	if (bp.availability == 0): return redirect('/dashboard')
	
	print "render_edit_lesson: lesson_id is", lesson_id
	
	lesson = Lesson.get_by_id(lesson_id)

	session_form = session.pop('form', None)
	session_errmsg = session.pop('errmsg', None)

	# Form will be none unless we are here after an unsuccessful form validation.
	if (session_form == None):
		print "render_edit_lesson: no form submitted - creating new"
		
		form = LessonForm(request.form)
		form.lessonTitle.data = lesson.lesson_title
		form.lessonDescription.data = lesson.lesson_description
		form.lessonAddress1.data = lesson.lesson_address_1
		form.lessonAddress2.data = lesson.lesson_address_2
		form.lessonCity.data = lesson.lesson_city
		form.lessonState.data = lesson.lesson_state
		form.lessonZip.data = lesson.lesson_zip
		form.lessonCountry.data = lesson.lesson_country
		form.lessonAddressDetails.data = lesson.lesson_address_details
		form.lessonRate.data = lesson.lesson_rate
		form.lessonRateUnit.data = lesson.lesson_rate_unit
		form.lessonPlace.data = lesson.lesson_loc_option
		form.lessonIndustry.data = lesson.lesson_industry
		form.lessonDuration.data = lesson.lesson_duration
		form.lessonAvail.data = lesson.lesson_avail
		form.lessonMakeLive.data = 'y'

		if (form.lessonRate.data <= 0):
			form.lessonRate.data = bp.prof_rate		

		if (lesson.lesson_flags == 2):
			form.lessonMakeLive.data = None

	else:
		# Submitted form didn't validate - repopulate from the submitted form instead of from the database.
		print "render_edit_lesson: invalid form imported"
		form = session_form
		errmsg = session_errmsg
		

	# lessonUpdated = lesson.lesson_updated

	return make_response(render_template('add_lesson.html', bp=bp, form=form, lesson_id=lesson_id, errmsg=errmsg, version="edit", lesson_title=lesson.lesson_title))


# Update will run no matter which form (add or edit) was submitted. It's the same function for both form types (i.e. there is no "create").
@insprite_views.route('/lesson/update/<lesson_id>', methods=['POST'])
@req_authentication
def api_update_lesson(lesson_id):
	bp = Profile.get_by_uid(session['uid'])
	if (bp.availability == 0): return redirect('/dashboard')
	
	version = request.values.get("version")
	saved = request.values.get("saved")
	print "api_update_lesson: Version is", version
	print "api_update_lesson: Saved is", saved
	print 'api_update_lesson: Beginning lesson update ...'

	form = LessonForm(request.form)
	lesson = Lesson.get_by_id(lesson_id)

	# If the form was saved, we don't need to validate - e.g. empty fields are ok.
	
	if (saved != "true"):

		# If the form is submitted, and it validates, do the update the database entry with this lesson
		if form.validate_on_submit():
			print 'api_update_lesson: valid POST'
			print 'api_update_lesson: lesson_id is ', lesson_id
			print 'api_update_lesson: looking for updates...'
			try:
				update_lesson = ht_update_lesson(lesson, form, saved)
				if (update_lesson):
					print 'api_update_lesson: updating lesson...'
					db_session.add(lesson)
					db_session.commit()
					print 'api_update_lesson: committed!'
			except Exception as e:
				print 'api_update_lesson: Exception:', type(e), e
				db_session.rollback()

			if (version == "save"):
				print "api_update_lesson: Returning to form"
				return jsonify(valid="true")
			else:
				print 'api_update_lesson: Redirecting to view lesson:', lesson_id
				return make_response(redirect("/lesson/"+lesson_id))

		else:
			print 'api_update_lesson: invalid POST', form.errors

	else:
		if form:

			# We need to know if it was a valid form. If it was not, we will mark the lesson as incomplete/saved.
			if form.validate_on_submit():
				print 'api_update_lesson: lesson was SAVED and it validated'
			else:
				print 'api_update_lesson: lesson was SAVED and it did NOT validate'
			
			print 'api_update_lesson: lesson_id is ', lesson_id
			print 'api_update_lesson: looking for updates...'
			try:
				update_lesson = ht_update_lesson(lesson, form, saved)
				if (update_lesson):
					print 'api_update_lesson: updating lesson...'
					db_session.add(lesson)
					db_session.commit()
					print 'api_update_lesson: committed!'
			except Exception as e:
				print 'api_update_lesson: Exception:', type(e), e
				db_session.rollback()			

			print "api_update_lesson: Returning to form"
			return jsonify(valid="true")

	if (saved != "true"):

		print 'api_update_lesson: fell through - populating form data and returning.'

		# This is messed up bc it is not accommodating an unsuccessful form submission - should take values from the form in that case, rather than from the database (where the lesson fields may be empty)

		# form.lessonTitle.data = lesson.lesson_title
		# form.lessonDescription.data = lesson.lesson_description
		# form.lessonAddress1.data = lesson.lesson_address_1
		# form.lessonAddress2.data = lesson.lesson_address_2
		# form.lessonCity.data = lesson.lesson_city
		# form.lessonState.data = lesson.lesson_state
		# form.lessonZip.data = lesson.lesson_zip
		# form.lessonCountry.data = lesson.lesson_country
		# form.lessonAddressDetails.data = lesson.lesson_address_details
		# form.lessonRate.data = lesson.lesson_rate
		# form.lessonRateUnit.data = lesson.lesson_rate_unit
		# form.lessonPlace.data = lesson.lesson_loc_option
		# form.lessonIndustry.data = lesson.lesson_industry
		# form.lessonDuration.data = lesson.lesson_duration
		# form.lessonAvail.data = lesson.lesson_avail
		# form.lessonMakeLive.data = 'y'

		# if (lesson.lesson_flags == 2):
		# 	form.lessonMakeLive.data = ''

		# lessonUpdated = lesson.lesson_updated
		# lessonCreated = lesson.lesson_created

		errmsg = "Sorry, something went wrong - your form didn't validate"
		print 'api_update_lesson: Here is the form data:', pprint(vars(form))

		session['form'] = form
		session['errmsg'] = errmsg

		if (version == "edit"):
			return redirect(url_for("insprite.render_edit_lesson", lesson_id=lesson_id))
		else:
			return redirect(url_for("insprite.render_new_lesson", lesson_id=lesson_id))




def ht_update_lesson(lesson, form, saved):
	print 'ht_update_lesson:', lesson
	print 'ht_update_lesson: saved? ', saved
	update = False
	for key in request.values:
		print '\t', key, request.values.get(key)
	print 'ht_update_lesson: save all updates'

	if (lesson.lesson_title != form.lessonTitle.data):
		print '\tUpdate lesson title (' + str(lesson.lesson_title) + ') => ' + str(form.lessonTitle.data)
		lesson.lesson_title = form.lessonTitle.data
		update = True

	if (lesson.lesson_description != form.lessonDescription.data):
		print '\tUpdate lesson desc (' + str(lesson.lesson_description) + ') => ' + str(form.lessonDescription.data)
		lesson.lesson_description = form.lessonDescription.data
		update = True

	if (lesson.lesson_loc_option != form.lessonPlace.data):
		print '\tUpdate lesson loc_option (' + str(lesson.lesson_loc_option) + ') => ' + str(form.lessonPlace.data)
		lesson.lesson_loc_option = form.lessonPlace.data
		update = True

	if (lesson.lesson_address_1 != form.lessonAddress1.data):
		print '\tUpdate lesson addr1(' + str(lesson.lesson_address_1) + ') => ' + str(form.lessonAddress1.data)
		lesson.lesson_address_1 = form.lessonAddress1.data
		update = True

	if (lesson.lesson_address_2 != form.lessonAddress2.data):
		print '\tUpdate lesson addr2(' + str(lesson.lesson_address_2) + ') => ' + str(form.lessonAddress2.data)
		lesson.lesson_address_2 = form.lessonAddress2.data
		update = True

	if (lesson.lesson_city	!= form.lessonCity.data):
		print '\tUpdate lesson city(' + str(lesson.lesson_city) + ') => ' + str(form.lessonCity.data)
		lesson.lesson_city	= form.lessonCity.data
		update = True

	if (lesson.lesson_state	!= form.lessonState.data):
		print '\tUpdate lesson state(' + str(lesson.lesson_state) + ') => ' + str(form.lessonState.data)
		lesson.lesson_state	= form.lessonState.data
		update = True

	if (lesson.lesson_zip != form.lessonZip.data):
		print '\tUpdate lesson zip(' + str(lesson.lesson_zip) + ') => ' + str(form.lessonZip.data)
		lesson.lesson_zip = form.lessonZip.data
		update = True

	if (lesson.lesson_address_details != form.lessonAddressDetails.data):
		print '\tUpdate lesson address details (' + str(lesson.lesson_address_details) + ') => ' + str(form.lessonAddressDetails.data)
		lesson.lesson_address_details = form.lessonAddressDetails.data
		update = True

	if (lesson.lesson_rate != form.lessonRate.data):
		print '\tUpdate lesson rate(' + str(lesson.lesson_rate) + ') => ' + str(form.lessonRate.data)
		lesson.lesson_rate = form.lessonRate.data
		update = True

	if (lesson.lesson_rate_unit != form.lessonRateUnit.data):
		print '\tUpdate lesson rate unit (' + str(lesson.lesson_rate_unit) + ') => ' + str(form.lessonRateUnit.data)
		lesson.lesson_rate_unit = form.lessonRateUnit.data
		update = True

	if (lesson.lesson_industry != form.lessonIndustry.data):
		print '\tUpdate lesson industry (' + str(lesson.lesson_industry) + ') => ' + str(form.lessonIndustry.data)
		lesson.lesson_industry = form.lessonIndustry.data
		update = True

	if (lesson.lesson_duration != form.lessonDuration.data):
		print '\tUpdate lesson duration (' + str(lesson.lesson_duration) + ') => ' + str(form.lessonDuration.data)
		lesson.lesson_duration = form.lessonDuration.data
		update = True

	if (lesson.lesson_avail != form.lessonAvail.data):
		print '\tUpdate lesson avail (' + str(lesson.lesson_avail) + ') => ' + str(form.lessonAvail.data)
		lesson.lesson_avail = form.lessonAvail.data
		update = True

	# Apply the flag logic
	# Default is 0 (initialized). If lesson has already been submitted, it will either be 2 (private) or 3 (active). 
	# It can also be saved (1) before it has been submitted. The saved state (1) implies incompleteness. Completeness validation will not happen for saved forms.
	# So if existing flag is 2 or 3, we will never set it to 1 (or zero), only back and forth between the two. Forms must be complete to be flagged 2 or 3.
	
	print "\tSetting Flags...current flag is",lesson.lesson_flags

	if (saved == "true"):
		print "\tUser saved form - set flag to 1 if not already 2 or 3"
		if (lesson.lesson_flags <= 1):
			lesson.lesson_flags = 1
			update = True
	elif (form.lessonMakeLive.data == True):
		print "\tUser submitted form and made live"
		lesson.lesson_flags = 3
		update = True
	else:
		print "\tUser submitted form but kept private"
		lesson.lesson_flags = 2
		update = True

	print "\tAnd now the flag is",lesson.lesson_flags	

	return update



# View the lesson page
@req_authentication
@insprite_views.route("/lesson/<lesson_id>", methods=['GET', 'POST'])
def render_lesson_page(lesson_id):
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])

	if (lesson_id is None):
		return make_response(render_dashboard(usrmsg='Need to specify a lesson...'))

	print "-"*36
	print "render_lesson_page(): Lesson ID:", lesson_id

	try:
		lesson = Lesson.get_by_id(lesson_id)
		portfolio = ht_get_serialized_images_for_lesson(lesson_id)
		print "render_lesson_page(): Lesson String:", str(lesson)
	except Exception as e:
		print 'render_lesson_page(): Exception Error:', e
		return make_response(render_dashboard(usrmsg='Can\'t find that lesson...'))
	return make_response(render_template('lesson.html', bp=bp, lesson=lesson, portfolio=portfolio))




@req_authentication
@insprite_views.route("/lesson/<lesson_id>/images", methods=['GET', 'POST'])
def api_get_images_for_lesson(lesson_id):
	# move this to API.

	try:
		images = ht_get_serialized_images_for_lesson(lesson_id)
	except Exception as e:
		print "api_get_images_for_lesson: exception:", type(e), e
		raise e
	return jsonify(portfolio=images)




@req_authentication
@insprite_views.route("/portfolio/<operation>/", methods=['POST'])
def api_update_portfolio(operation):
	bp = Profile.get_by_uid(session['uid'])
	lesson_id = request.values.get('lesson_id')

	print "-"*24
	print "api_update_portfolio(): operation:", operation

	try:
		# get portfolio.
		portfolio = None

		# get lesson-portfolio imgs
		print "api_update_portfolio(): Couldn't find Lesson."
		portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (operation == 'add'):
		print 'api_update_portfolio(): adding file'
	elif (operation == 'update'):
		print 'api_update_portfolio(): usr request: update portfolio'
		try:
			for img in portfolio:
				update = False;
				print "\tPortfolio Image:", img, img.img_id
				jsn = request.values.get(img.img_id)
				if jsn is None:
					print img.img_id, 'doesnt exist in user-set, deleted.'
					db_session.delete(img)
					continue

				obj = json.loads(jsn)
				print img.img_id, obj['idx'], obj['cap']
				if (img.img_order != obj['idx']):
					update = True
					print 'update img_order'
					img.img_order = int(obj['idx'])
				if (img.img_comment != obj['cap']):
					update = True
					print 'update img_cap'
					img.img_comment = obj['cap']

				if (update): db_session.add(img)

			db_session.commit()
		except Exception as e:
			print type(e), e
			db_session.rollback()
			return jsonify(usrmsg='This is embarassing.  We failed'), 500

		return jsonify(usrmsg='Writing a note here: Huge Success'), 200
	else:
		return jsonify(usrmsg='Unknown operation.'), 500




@req_authentication
@insprite_views.route("/lesson/<lesson_id>/image/update", methods=['POST'])
def api_lesson_image_update(lesson_id):
	bp = Profile.get_by_uid(session['uid'])

	print 'api_lesson_image_update(): usr request: update portfolio'
	if (lesson_id is None):
		print "api_lesson_image_update(): Couldn't find Lesson."
		return jsonify(usrmsg="no lesson specified")

	try:
		# get lesson-portfolio imgs
		portfolio = htdb_get_lesson_images(lesson_id)
		print 'api_lesson_image_update():', len(portfolio)

		for lesson_map in portfolio:
			update = False;
			print "api_lesson_image_update()\tlook for lesson image:", lesson_map.map_image
			img = request.values.get(lesson_map.map_image, None)
			if img is None:
				print 'api_lesson_image_update()\t', lesson_map.map_image, 'doesnt exist in user-set, deleted.'
				db_session.delete(lesson_map)
				continue

			obj = json.loads(img)
			print lesson_map.map_image, obj['idx'], obj['cap']
			if (lesson_map.map_order != obj['idx']):
				update = True
				print 'api_lesson_image_update()\tupdate img_order'
				lesson_map.map_order = int(obj['idx'])

			if (lesson_map.map_comm != obj['cap']):
				update = True
				print 'api_lesson_image_update()\tupdate img caption'
				lesson_map.map_comm = obj['cap']

			if (update): db_session.add(lesson_map)
		db_session.commit()

	except Exception as e:
		print type(e), e
		db_session.rollback()
		return jsonify(usrmsg='This is embarassing.  We failed'), 500
	return make_response(jsonify(usrmsg='Writing a note here: Huge Success'))





@insprite_views.route('/schedule', methods=['GET','POST'])
@req_authentication
def render_schedule_page():
	""" Schedule a new appointment appointment. """

	usrmsg = None
	try:
		bp = Profile.get_by_uid(session.get('uid'))
		ba = Account.get_by_uid(session.get('uid'))
		hp = Profile.get_by_prof_id(request.values.get('hp', None))
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (hp is None):
		return redirect(url_for('insprite.render_dashboard', messages='You must specify a user profile to scheduling.'))

	if (ba.status == Account.USER_UNVERIFIED):
		session['messages'] = 'We require a verified email prior to scheduling'
		return make_response(redirect(url_for('insprite.render_settings', nexturl='/schedule?hp='+request.args.get('hp'))))

	nts = NTSForm(request.form)
	nts.hero.data = hp.prof_id
	print 'render_schedule()\tusing STRIPE: ', ht_server.config['STRIPE_SECRET']

	return make_response(render_template('schedule.html', bp=bp, hp=hp, form=nts, STRIPE_PK=ht_server.config['STRIPE_PUBLIC'], buyer_email=ba.email, errmsg=usrmsg))




@insprite_views.route("/review/new/<review_id>", methods=['GET', 'POST'])
@req_authentication
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




@insprite_views.route('/settings', methods=['GET', 'POST'])
@req_authentication
def render_settings():
	print 'render_settings()\t enter'
	""" Provides users the ability to modify their settings."""
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	ba	= Account.get_by_uid(uid)
	pi	= Oauth.get_stripe_by_uid(uid)


	# StripeConnect allows a user to charge customers.
	stripe_connect = 'StripeConnect account not found.'
	if (pi is not None): stripe_connect = pi.oa_account

	errmsg = None
	insprite_msg = session.pop('messages', None)

	form = SettingsForm(request.form)
	if form.validate_on_submit():
		print 'render_settings()\tvalid submit'
		update_acct = False		# requires current_pw_set, 					Sends email
		update_pass = None		# requires current_pw_set, valid new pw =>	Sends email
		update_mail = None
		update_name = None

		update_prop = None
		update_vnty = None
		update_fail = False

		if (form.set_input_name.data != ba.name):
			print 'render_settings()\tupdate', str(ba.name) + " to " +  str(form.set_input_name.data)
			update_acct = True
			update_name = form.set_input_name.data

		if (form.set_input_newpass.data != ""):
			print 'render_settings()\tupdate', str(ba.pwhash) + " to " +  str(form.set_input_newpass.data)
			update_acct = True
			update_pass = form.set_input_newpass.data

		if (ba.email != form.set_input_email.data):
			print 'render_settings()\tupdate', str(ba.email) + " to " +  str(form.set_input_email.data)
			update_acct = True
			update_mail = form.set_input_email.data

		if (update_acct):
			print 'render_settings()\tupdate account'
			if (update_pass):
				pwd = form.set_input_curpass.data
			else:
				pwd = form.set_input_email_pass.data
			print 'render_settings()\tnow call modify account()'
			(rc, errno) = modifyAccount(uid, pwd, new_pass=update_pass, new_mail=update_mail)
			print("render_settings()\tmodify acct()  = " + str(rc) + ", errno = " + str(errno))
			if (rc == False):
				errmsg = str(errno)
				errmsg = error_sanitize(errmsg)
				form.set_input_curpass.data = ''
				form.set_input_newpass.data = ''
				form.set_input_verpass.data = ''
				return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
			else:
				print "render_settings() Update should be complete"

		if (update_mail):
			# user changed email; for security, send confimration email to last email addr.
			ht_send_email_address_changed_confirmation(ba.email, form.set_input_email.data)
			errmsg = "Your email has been updated."

		#change pass send email
		if (update_pass):
			send_passwd_change_email(ba.email)
			errmsg = "Password successfully updated."

		print 'render_settings() Finished Handling POST.'
	elif request.method == 'GET':
		print 'render_settings()\t GET'
	else:
		print 'render_settings()\t invalid submit' , form.errors
		errmsg = "Passwords must match."


	email_unver = False
	if (ba.status == Account.USER_UNVERIFIED):
		email_unver = True
	print 'render_settings()', bp.prof_name, ' email unverified', email_unver

	form.oauth_stripe.data	= stripe_connect
	form.set_input_email.data	= ba.email
	form.set_input_name.data	= ba.name
	nexturl = "/settings"
	if (request.values.get('nexturl') is not None):
		nexturl = request.values.get('nexturl')
	if (errmsg is None): errmsg = insprite_msg

	return make_response(render_template('settings.html', form=form, bp=bp, nexturl=nexturl, unverified_email=email_unver, errmsg=errmsg))




# rename /image/create
@insprite_views.route('/upload', methods=['POST'])
@dbg_enterexit
@req_authentication
def upload():
	log_uevent(session['uid'], " uploading file")

	bp = Profile.get_by_uid(session.get('uid'))
	orig = request.values.get('orig')
	prof = request.values.get('prof')
	update_profile_img = request.values.get('profile', False)
	lesson_id = request.values.get('lessonID')

	print 'upload: orig', orig
	print 'upload: prof', prof
	print 'upload: lesson_id', lesson_id

	for mydict in request.files:
		# for sec. reasons, ensure this is 'edit_profile' or know where it comes from
		print("upload()\treqfiles[" + str(mydict) + "] = " + str(request.files[mydict]))
		image_data = request.files[mydict].read()
		print ("upload()\timg_data type = " + str(type(image_data)) + " " + str(len(image_data)) )

		if (len(image_data) > 0):
			image = ht_create_image(bp, image_data, comment="No caption")

			if (lesson_id):
				print 'upload()\tlesson_id' + str(lesson_id)
				ht_map_image_to_lesson(image, lesson_id)

			if (update_profile_img):
				print 'upload()\tupdate profile img'
				bp.update_profile_image(image)

	return jsonify(tmp="/uploads/" + str(image.img_id))





#HELPER FUNCTIONS.

@insprite_views.route('/uploads/<filename>')
def uploaded_file(filename):
	# add sec protection?
	return send_from_directory(ht_server.config['HT_UPLOAD_DIR'], filename)



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
			db_session.add(image)
			db_session.commit()
		except IntegrityError as ie:
			# image already exists.
			print 'upload()\tht_image_create() funny seeing image already exist here.'
			print 'upload: exception', type(e), e
			db_session.rollback()
		except Exception as e:
			print 'upload: exception', type(e), e
			db_session.rollback()
	return image



def ht_upload_image_to_S3(image, image_data):
	f = open(os.path.join(ht_server.config['HT_UPLOAD_DIR'], image.img_id), 'w')
	f.write(image_data)
	f.close()

	print 'upload()\tupload_image_to_S3\tpush image to S3.'
	s3_con = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"])
	s3_bkt = s3_con.get_bucket(ht_server.config["S3_BUCKET"])
	s3_key = s3_bkt.new_key(ht_server.config["S3_DIRECTORY"] + image.img_id)
	print 'upload()\tupload_image_to_S3\tcreated s3_key.'
	s3_key.set_contents_from_file(StringIO(image_data))




def ht_map_image_to_lesson(image, lesson_id):
	print 'upload()\tmap_image_to_lesson\t', image.img_id, ' <=> ', lesson_id

	print 'upload()\tmap_image_to_lesson\t Does map exist?'
	map_exists = LessonImageMap.exists(image.img_id, lesson_id)
	if (map_exists):
		print 'upload()\tmap_image_to_lesson\t yes map already exists'
		return

	li_map = LessonImageMap(image.img_id, lesson_id, image.img_profile, comment=image.img_comment)
	try:
		db_session.add(li_map)
		db_session.commit()
		print 'upload()\tmap_image_to_lesson\tcommitted'
	except Exception as e:
		print type(e), e
		db_session.rollback()




def ht_get_serialized_images_for_lesson(lesson_id):
	# json_serialize all images assoicated with the lesson.
	images = LessonImageMap.get_images_for_lesson(lesson_id)
	return [img.serialize for img in images]




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
