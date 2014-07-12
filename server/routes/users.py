#################################################################################
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
from server.infrastructure.models import *
from server.controllers import *
from . import insprite_views
from .api import ht_api_get_message_thread
from .helpers import *
from ..forms import ProfileForm, SettingsForm, NTSForm, ReviewForm

# more this into controllers / tasks.
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug          import secure_filename
from StringIO import StringIO



@insprite_views.route('/home',      methods=['GET', 'POST'])
@insprite_views.route('/dashboard', methods=['GET', 'POST'])
@req_authentication
def render_dashboard(usrmsg=None):
	""" Provides Hero their personalized homepage.
		- Show calendar with all upcoming appointments
		- Show any statistics.
	"""

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	print 'render_dashboard() profile.account = ', bp.prof_name, uid

	unread_msgs = []

	try:
		(props, appts, rview) = ht_get_active_meetings(bp)
		active_reviews = ht_get_active_author_reviews(bp)
		unread_msgs = ht_get_unread_messages(bp)
		lessons = ht_get_lessons(bp)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	
	map(lambda msg: display_partner_message(msg, bp.prof_id), unread_msgs)
	return make_response(render_template('dashboard.html', title="- " + bp.prof_name, bp=bp, lessons=lessons, proposals=props, appointments=appts, messages=unread_msgs, reviews=active_reviews, errmsg=usrmsg))




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
@ht_server.route("/get_threads", methods=['GET', 'POST'])
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
	lesson_id = request.values.get('lesson_id')

	if (lesson_id is not None):
		print "render_edit_portfolio_page(): Lesson ID:", lesson_id
		portfolio = db_session.query(Image).filter(Image.img_lesson == lesson_id).all()
	else:
		print "render_edit_portfolio_page(): get all images for profile:"
		portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))




@ht_server.route('/seller_signup', methods=['GET', 'POST'])
@req_authentication
def render_seller_signup_page(usrmsg = None):
	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	pi = Oauth.get_stripe_by_uid(uid)

	stripe = 'None'
	# Stripe Connect ID, req'd to take payments
	if (pi is not None): stripe = pi.oa_account

	session['next_url']='/seller_signup#payment'
	return make_response(render_template('seller_signup.html', title='- Sign Up to Teach', bp=bp, oa_stripe=stripe))




@ht_server.route('/activate_seller', methods=['GET', 'POST'])
@req_authentication
def activate_seller():
	""" A regular user is signing up to be a seller.  """

	print "-"*32
	print 'activate_seller(): begin'
	uid = session['uid']
	bp = Profile.get_by_uid(session.get('uid'))
	ba = Account.get_by_uid(session.get('uid'))
	form = ProfileForm(request.form)

	# TODO - put this back in
	# if form.validate_on_submit():

	try:
		bp.avail = int(form.ssAvailOption.data)
		bp.stripe_cust = form.oauth_stripe.data
		ba.role = 1

		# TODO: re-enable this; fails on commit (can't compare offset-naive and offset-aware datetimes)
		# bp.updated  = dt.utcnow()

		# check for photo - if seller is uploading new one, we replace their old prof_img with it.
		# TODO: what happens if someone wants to just keep their old one?
		image_data = request.files[form.ssProfileImage.name].read()
		if (len(image_data) > 0):
			destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			trace (destination_filename + ", sz = " + str(len(image_data)))
			print 'activate_seller(): s3'
			conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"])
			b = conn.get_bucket(ht_server.config["S3_BUCKET"])
			sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
			sml.set_contents_from_file(StringIO(image_data))
			bp.prof_img = destination_filename

		print 'activate_seller(): add'
		db_session.add(bp)
		db_session.add(ba)
		print 'activate_seller(): commit'
		db_session.commit()
		log_uevent(uid, "activate seller profile")

		return make_response(redirect(url_for('render_dashboard')))

	except AttributeError as ae:
		print 'activate_seller(): hrm. must have changed an object somehwere'
		print ae
		db_session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500

	except Exception as e:
		print e
		db_session.rollback()
		return jsonify(usrmsg=e), 500




@ht_server.route('/lesson/create', methods=['GET', 'POST'])
@req_authentication
def ht_api_lesson_create():
	user_message = 'Initializing Lesson...'
	bp = Profile.get_by_uid(session['uid'])

	print "ht_api_lesson_create: bp is",bp
	print "ht_api_lesson_create: bp.prof_id is",bp.prof_id

	try:
		lesson = ht_create_lesson()
		print 'ht_api_lesson_create: lesson id is', lesson.lesson_id
		if (lesson is not None):
			lesson_id = lesson.lesson_id
			print 'ht_api_lesson_create: Successfully initialized lesson'
		else:
			print 'ht_api_lesson_create: Error initializing lesson'

	except Sanitized_Exception as se:
		user_message = se.get_sanitized_msg()
		print 'ht_api_lesson_create: sanitized exception:', user_message, se.httpRC()
		print
		return make_response(jsonify(usrmsg=user_message), se.httpRC())

	except Exception as e:
		print 'ht_api_lesson_create: exception:', type(e), e
		print
		return make_response(jsonify(usrmsg='Something bad'), 500)

	return make_response(render_template('add_lesson.html', lesson_id=lesson_id, bp=bp))




@ht_server.route('/create_lesson/<lesson_id>', methods=['POST'])
@req_authentication
def create_lesson(lesson_id):
	""" We have initialized a lesson already in /lesson/create - we will now add the details """

	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	form = request.form

	print "-"*32
	print "Creating Lesson...\n"
	print "Here's the form data:", str(form)
	print "The Lesson ID: ",lesson_id

	# if form.validate_on_submit():
	try:
		lesson = Lesson.get_by_lesson_id(lesson_id)
		lesson.lesson_title = request.form.get('addLessonTitle')
		lesson.lesson_description = request.form.get('addLessonDescription')
		lesson.lesson_industry = request.form.get('addLessonIndustry')
		lesson.lesson_unit = request.form.get('addLessonRateUnit')

		if (lesson.lesson_unit == "perHour"):
			try:
			   lesson.lesson_hourly_rate = int(request.form.get('addLessonRate'))
			except ValueError:
			   pass
		else:
			try:
			   lesson.lesson_lesson_rate = int(request.form.get('addLessonRate'))
			except ValueError:
			   pass

		lesson.lesson_avail = request.form.get('addLessonAvail')

		try:
		   lesson.lesson_duration	= int(request.form.get('addLessonDuration'))
		except ValueError:
		   pass

		lesson.lesson_loc_option = request.form.get('addLessonPlace')
		lesson.lesson_address_1 = request.form.get('addLessonAddress1')
		lesson.lesson_address_2 = request.form.get('addLessonAddress2')
		lesson.lesson_city = request.form.get('addLessonCity')
		lesson.lesson_state = request.form.get('addLessonState')
		lesson.lesson_zip = request.form.get('addLessonZip')
		lesson.lesson_country = request.form.get('addLessonCountry')
		lesson.lesson_address_details = request.form.get('addLessonAddressDetails')

		# This maybe doesn't work? Leaving out for now
		# lesson.lesson_updated = dt.utcnow()

		if (request.form.get('addLessonSave') == "True"):
			lesson.lesson_flags = lesson.lesson_flags | LESSON_FLAG_SAVED
		elif (request.form.get('addLessonMakeLive') == "True"):
			lesson.lesson_flags = lesson.lesson_flags | LESSON_FLAG_ACTIVE
		else:
			lesson.lesson_flags = lesson.lesson_flags | LESSON_FLAG_PRIVATE

		print 'adding lesson: ', lesson.lesson_id, lesson.lesson_title, lesson.lesson_industry, lesson.lesson_flags
		db_session.add(lesson)
		print 'committing...'
		db_session.commit()
		log_uevent(uid, "create lesson")

		return make_response(render_lesson_page(lesson_id))

	except AttributeError as ae:
		print 'Attribute Error'
		print ae
		db_session.rollback()
		return make_response(render_template('add_lesson.html', lesson_id=lesson.lesson_id, usrmsg="We messed something up"))

	except Exception as e:
		print 'Exception Error'
		print e
		db_session.rollback()
		return make_response(render_template('add_lesson.html', lesson_id=lesson.lesson_id, usrmsg=e))




@req_authentication
@ht_server.route("/lesson", methods=['GET', 'POST'])
def render_lesson_page(lesson_id=None):
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])

	if (lesson_id == None):
		lesson_id = request.values.get('lesson_id')

	print "-"*36
	print "render_lesson_page(): Lesson ID:", lesson_id

	try:
		lesson = Lesson.get_by_lesson_id(lesson_id)
		portfolio = db_session.query(Image).filter(Image.img_lesson == lesson_id).all()

		print "render_lesson_page(): Lesson String:", str(lesson)
		print "render_lesson_page(): Images:", str(portfolio)

		return make_response(render_template('lesson.html', bp=bp, lesson=lesson, portfolio=portfolio))

	except Exception as e:
		print 'render_lesson_page(): Exception Error:', e
		return make_response(render_dashboard(usrmsg='Can\'t find that lesson...'))




@req_authentication
@insprite_views.route("/get_lesson_images", methods=['GET', 'POST'])
def get_lesson_images():
	# move this to API.
	lesson_id = request.values.get('lesson_id')
	images = []

	try:
		print "get_lesson_images: lesson_id is", lesson_id
		images = db_session.query(Image).filter(Image.img_lesson == lesson_id).all();
		json_images = [img.serialize for img in images]
	except Exception as e:
		print "get_lesson_images: exception:", e
		json_images = None
	return jsonify(images=json_images)




@req_authentication
@insprite_views.route("/portfolio/<operation>/", methods=['POST'])
def ht_api_update_portfolio(operation):
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	lesson_id = request.values.get('lesson_id')

	print "-"*24
	print "ht_api_update_portfolio(): operation:", operation
	print "ht_api_update_portfolio(): lesson_id:", lesson_id

	try:
		# get portfolio.
		portfolio = None
		# PRE-LESSONS # portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()

		# get lesson-portfolio imgs
		if (lesson_id is not None):
			portfolio = db_session.query(Image).filter(Image.img_lesson == lesson_id).all()
		else:
			print "ht_api_update_portfolio(): Couldn't find Lesson."
			#
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (operation == 'add'):
		print 'ht_api_update_portfolio(): adding file'
	elif (operation == 'update'):
		print 'ht_api_update_portfolio(): usr request: update portfolio'
		images = request.values.get('images')
		print "ht_api_update_portfolio(): images:", str(images)

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




@insprite_views.route('/schedule', methods=['GET','POST'])
@req_authentication
def render_schedule_page():
	""" Schedule a new appointment appointment. """

	usrmsg = None
	try:
		hp_id = request.values.get('hp', None)
		bp = Profile.get_by_uid(session.get('uid'))
		hp = Profile.get_by_prof_id(request.values.get('hp', None))
		ba = Account.get_by_uid(session.get('uid'))
	except Exception as e:
		db_session.rollback()

	if (ba.status == Account.USER_UNVERIFIED):
		return make_response(redirect(url_for('insprite.render_settings', nexturl='/schedule?hp='+request.args.get('hp'), messages='You must verify email before scheduling.')))

	nts = NTSForm(request.form)
	nts.hero.data = hp.prof_id

	return make_response(render_template('schedule.html', bp=bp, hp=hp, form=nts, errmsg=usrmsg))




@insprite_views.route("/review/<meet_id>/<review_id>", methods=['GET', 'POST'])
@req_authentication
def render_review_meeting_page(meet_id, review_id):
	uid = session['uid']

	print 'render_review()\tenter'
	# if its been 30 days since review creation.  Return an error.
	# if review already exists, return a kind message.

	try:
		print 'render_review()\t', 'meeting =', meet_id, '\treview_id =', review_id
		review = Review.get_by_id(review_id)
		bp = Profile.get_by_uid(session['uid'])
		ba = Account.get_by_uid(bp.account)
		rp = Profile.get_by_prof_id(review.prof_reviewed)	# reviewed  profile
		print 'render_review()\t, author =', bp.prof_id, bp.prof_name, ba.email
		print 'render_review()\t, review author =', review.prof_authored
		print 'render_review()\t, review revied =', review.prof_reviewed
		print review

		review.validate(bp.prof_id)
		print 'we\'re the intended audience'

		print review.prof_authored
		print uid
		print dt.utcnow()


		days_since_created = timedelta(days=30) # + review.rev_updated - dt.utcnow()  #CAH FIXME TODO
		#appt = Appointment.query.filter_by(apptid=review.appt_id).all()[0]
		#show the -cost, -time, -description, -location
		#	were you the buyer or seller.  the_appointment.hero; the_appointment.sellr_prof

		review_form = ReviewForm(request.form)
		review_form.review_id.data = str(review_id)
		return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=rp, daysleft=str(days_since_created.days), form=review_form))

	except NoReviewFound as rnf:
		print rnf 
		db_session.rollback()
		return jsonify(usrmsg=rnf.msg)
	except ReviewError as re:
		print re
		db_session.rollback()
		return jsonify(usrmsg=re.msg)
	except Exception as e:
		print e
		db_session.rollback()
		return redirect('/failure')
	except IndexError as ie:
		print 'trying to access, review, author or reviewer account and fialed'
		db_session.rollback()
		return redirect('/dbFailure')



@insprite_views.route('/settings', methods=['GET', 'POST'])
@req_authentication
def render_settings():
	""" Provides users the ability to modify their settings.
		- detect HT Session info.  Provide modified info.
	"""
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	ba	= Account.get_by_uid(uid)
	pi	= Oauth.get_stripe_by_uid(uid)

	card = 'Null'
	if (pi is not None):
		#pp(pi.serialize)
		# Not a Customer.  Customers exist in Accounts.
		# This is the Stripe Connect ID.  Own business.
		# We use the pub & secret keys to charge users
		card = pi.oa_account

	errmsg = None
	form = SettingsForm(request.form)
	if form.validate_on_submit():
		update_acct = False		# requires current_pw_set, 					Sends email
		update_pass = None		# requires current_pw_set, valid new pw =>	Sends email
		update_mail = None

		update_prof = False		# do nothing if above are set.
		update_prop = None
		update_vnty = None
		update_fail = False

		if (form.set_input_newpass.data != ""):
			trace("attempt update pass " + str(ba.pwhash) + " to " +  str(form.set_input_newpass.data))
			update_acct = True
			update_pass = form.set_input_newpass.data

		if (ba.email != form.set_input_email.data):
			trace("attempt update email "  + str(ba.email) +  " to " + str(form.set_input_email.data))
			update_acct = True
			update_mail = form.set_input_email.data

		if (update_acct):
			if (update_pass):
				pwd = form.set_input_curpass.data
			else:
				pwd = form.set_input_email_pass.data
			trace("password is: " + pwd)
			(rc, errno) = modifyAccount(uid, pwd, new_pass=update_pass, new_mail=update_mail)
			trace("modify acct = " + str(rc) + ", errno = " + str(errno))
			if (rc == False):
				trace("restate errno" + str(errno))
				errmsg = str(errno)
				errmsg = error_sanitize(errmsg)
				form.set_input_curpass.data = ''
				form.set_input_newpass.data = ''
				form.set_input_verpass.data = ''
				return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
			else:
				print "Update should be complete"

		if (update_prof):
			try:
				print "update prof"
				db_session.add(bp)
				db_session.commit()
				trace("commited plus email is : " + update_mail)
			except Exception as e:
				db_session.rollback()
				return redirect('/dbFailure')


		#change email; send email to both.
		if (update_mail):
			ht_email_confirmation_of_changed_email_address(ba.email, form.set_input_email.data)
			errmsg = "Your email has been updated."

		#change pass send email
		if (update_pass):
			send_passwd_change_email(ba.email)
			errmsg = "Password successfully updated."

		return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
	elif request.method == 'GET':
		msg = request.values.get('messages')
		if (msg is not None): errmsg = msg
	else:
		print "form isnt' valid"
		print form.errors
		errmsg = "Passwords must match."


	email_unver = False
	if (ba.status == Account.USER_UNVERIFIED):
		print bp.prof_name, ' email is unverified'
		email_unver = True

	form.oauth_stripe.data     = card
	form.set_input_email.data  = ba.email
	nexturl = "/settings"
	if (request.values.get('nexturl') is not None):
		nexturl = request.values.get('nexturl')

	return make_response(render_template('settings.html', form=form, bp=bp, nexturl=nexturl, unverified_email=email_unver, errmsg=errmsg))



@insprite_views.route('/upload', methods=['POST'])
@dbg_enterexit
@req_authentication
def upload():
	log_uevent(session['uid'], " uploading file")
	#trace(request.files)

	bp = Profile.get_by_uid(session.get('uid'))
	orig = request.values.get('orig')
	prof = request.values.get('prof')
	lesson_id = request.values.get('lesson_id')

	print 'upload: orig', orig
	print 'upload: prof', prof
	print 'upload: lesson_id', lesson_id

	for mydict in request.files:

		comment = ""

		# for sec. reasons, ensure this is 'edit_profile' or know where it comes from
		print("upload: reqfiles[" + str(mydict) + "] = " + str(request.files[mydict]))
		image_data = request.files[mydict].read()
		print ("upload: img_data type = " + str(type(image_data)) + " " + str(len(image_data)) )

		#trace ("img_data type = " + str(type(image_data)) + " " + str(len(image_data)) )
		if (len(image_data) > 0):
			# create Image.
			img_hashname = secure_filename(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			metaImg = Image(img_hashname, bp.prof_id, comment, lesson_id)
			f = open(os.path.join(ht_server.config['HT_UPLOAD_DIR'], img_hashname), 'w')
			f.write(image_data)
			f.close()
			try:
				print 'upload: adding metaimg to db'
				db_session.add(metaImg)
				db_session.commit()
			except Exception as e:
				print 'upload: exception', type(e), e
				db_session.rollback()

		# upload to S3.
		conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
		b = conn.get_bucket(ht_server.config["S3_BUCKET"])
		sml = b.new_key(ht_server.config["S3_DIRECTORY"] + img_hashname)
		sml.set_contents_from_file(StringIO(image_data))

	return jsonify(tmp="/uploads/" + str(img_hashname))





#HELPER FUNCTIONS.

@insprite_views.route('/uploads/<filename>')
def uploaded_file(filename):
	# add sec protection?
	return send_from_directory(ht_server.config['HT_UPLOAD_DIR'], filename)


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
