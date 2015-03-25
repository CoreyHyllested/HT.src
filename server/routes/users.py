################################################################################
# Copyright (C) 2015 Soulcrafting.
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


from server.ht_utils import *
from server.infrastructure.srvc_database import db_session
from server.models import *
from server.infrastructure.errors import *
from server.controllers import *
from . import sc_users
from .api import ht_api_get_message_thread
from .helpers import *
from ..forms import ProfileForm, ProjectForm, SettingsForm, ReviewForm
from ..forms import InviteForm, ProposalForm, GiftForm

# more this into controllers / tasks.
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug          import secure_filename
from StringIO import StringIO
from pprint import pprint
import os
from datetime import datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@sc_users.route('/dashboard/', methods=['GET', 'POST'])
@sc_users.route('/dashboard', methods=['GET', 'POST'])
@req_authentication
def render_dashboard(usrmsg=None):
	bp = Profile.get_by_uid(session['uid'])
	insprite_msg = session.pop('messages', None)
	print 'render_dashboard(' + bp.prof_name + ',' + session['uid'] + ')'
	usercash = None

	try:
		projects = sc_get_projects(bp)
		for p in projects:
			pprint(p)
		usercash = GiftCertificate.get_user_credit_amount(bp)
		print usercash
		#(props, appts, rview) = ht_get_active_meetings(bp)
	except Exception as e:
		print 'render_dashboard() tries failed -  Exception: ', type(e), e
		db_session.rollback()
	
	if (usrmsg is None and insprite_msg):
		usrmsg = insprite_msg
		print 'render_dashboard() usrmsg = ', usrmsg

	print 'render_dashboard()'
	return make_response(render_template('dashboard.html', bp=bp, projects=projects, credit=usercash, errmsg=usrmsg))




@sc_users.route('/invite', methods=['GET', 'POST'])
@req_authentication
def render_invite_page():
	bp = Profile.get_by_uid(session['uid'])
	ba = Account.get_by_uid(session['uid'])

	invite = InviteForm(request.form)
	invite.invite_userid.data = bp.account
	if invite.validate_on_submit():
		try:
			print 'invite: valid post from user ', invite.invite_userid.data, invite.invite_emails.data

			print 'invite: create gift'
			r = {}
			r['mail'] = invite.invite_emails.data
			r['name'] = 'Unknown'
			p = {}
			p['prof'] = bp.prof_id
			p['name'] = bp.prof_name
			p['mail'] = ba.email
			p['cost'] = 0
			s = {}
			s['gift_value'] = 15000		# $150.00
			gift = GiftCertificate(r, p, s)
			print gift

			referral = Referral(bp.account, gift_id=gift.gift_id)
			print referral

			db_session.add(gift)
			db_session.add(referral)
			db_session.commit()
#			print 'invite: check post from user personalized', invite.invite_personalized.data
			sc_email_invite_friend(invite.invite_emails.data, friend_name=bp.prof_name, referral_id=referral.ref_id, gift_id=bp.account)
			return redirect('/dashboard')

		except Exception as e:
			print e
			db_session.rollback()
			print 'need to set error message and post to user'
	elif request.method == 'POST':
		print 'invite: invalid POST', invite.errors
	else:
		pass

	print 'render_invite(): render page'
	return make_response(render_template('invite.html', bp=bp, form=invite))




@sc_users.route("/purchase_me", methods=['GET', 'POST'])
@req_authentication
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






#@insprite_views.route('/profile/edit', methods=['GET', 'POST'])
#@req_authentication
def render_edit_profile():
	# Form to edit a profile

	bp = Profile.get_by_uid(session['uid'])
	ba = Account.get_by_uid(session['uid'])
	avail = Availability.get_by_prof_id(bp.prof_id)

	# Days array for avail
	d = {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}

	# StripeConnect req'd for payments
	pi = Oauth.get_stripe_by_uid(session['uid'])
	stripe = ''
	if (pi is not None): stripe = pi.oa_account
	
	# session_form = session.pop('form', None)
	# session_errmsg = session.pop('errmsg', None)
	
	# Set session next_url here
	# session['next_url'] = '/profile/edit#payment'

	form = ProfileForm(request.form)
	x = 0
	for x in range(len(Industry.industries)):
		if Industry.industries[x] == bp.industry:
			form.edit_industry.data = str(x)
			break

	form.edit_name.data     = bp.prof_name
	form.edit_location.data = bp.location	
	form.edit_bio.data      = bp.prof_bio
	form.edit_headline.data = bp.headline
	form.edit_industry.data = str(x)
	form.edit_url.data      = bp.prof_url
	form.edit_rate.data     = bp.prof_rate
	form.edit_availability.data      = bp.availability
	form.edit_oauth_stripe.data 	 = stripe

	slotdays = []

	for timeslot in avail:
		print "weekday is", timeslot.avail_weekday
		print "start is", timeslot.avail_start
		print "finish is", timeslot.avail_finish
		
		day = timeslot.avail_weekday

		# # Create variable strings for each start/end time and the day, define them as variables with vars(), and set their values. 
		# start = "form.edit_avail_time_"+day+"_start.data"
		# finish = "form.edit_avail_time_"+day+"_end.data"
		# day = "form.edit_avail_day_"+day+".data"

		if (day == 0):
			form.edit_avail_time_sun_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_sun_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_sun.data = 'y'

		if (day == 1):
			form.edit_avail_time_mon_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_mon_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_mon.data = 'y'		

		if (day == 2):
			form.edit_avail_time_tue_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_tue_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_tue.data = 'y'

		if (day == 3):
			form.edit_avail_time_wed_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_wed_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_wed.data = 'y'

		if (day == 4):
			form.edit_avail_time_thu_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_thu_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_thu.data = 'y'

		if (day == 5):
			form.edit_avail_time_fri_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_fri_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_fri.data = 'y'

		if (day == 6):
			form.edit_avail_time_sat_start.data = str(timeslot.avail_start)[:-3]
			form.edit_avail_time_sat_finish.data = str(timeslot.avail_finish)[:-3]
			form.edit_avail_day_sat.data = 'y'

	flags = bp.availability
	print "render_edit_profile(): This user's availability is ", bp.availability

	photoURL = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(bp.prof_img)


	return make_response(render_template('edit_profile.html', title="- Edit Profile", form=form, bp=bp, photoURL=photoURL, flags=flags))


#@insprite_views.route('/profile/update', methods=['POST'])
#@req_authentication
def api_update_profile(usrmsg=None):
	# Process the edit profile form

	print "api_update_profile: beginning update"

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	ba = Account.get_by_uid(uid)
	

	form_mode = request.values.get('formMode');
	form_page = request.values.get('formPage');
	form = ProfileForm(request.form)

	print "api_update_profile: form mode: ", form_mode
	print "api_update_profile: form page: ", form_page

	# we will validate each submitted page manually so as to allow for partial form submission (not using WTForm validation.)

	try:
		page_validate, errors = ht_validate_profile(bp, form, form_page)

		if (page_validate):
			update = ht_update_profile(ba, bp, form, form_page)
			if (update):
				print 'api_update_profile: add'
				db_session.add(bp)
				db_session.add(ba)
				print 'api_update_profile: commit'
				db_session.commit()
				log_uevent(uid, "update profile")
				return jsonify(usrmsg="profile updated"), 200
			else:
				db_session.rollback()
				print 'api_update_profile: update error.'
				return jsonify(usrmsg="We messed something up, sorry"), 500

		return jsonify(usrmsg='Sorry, some required info was missing or in an invalid format. Please check the form.', errors=errors), 500

	except AttributeError as ae:
		print 'api_update_profile: hrm. must have changed an object somehwere'
		print 'api_update_profile: AttributeError: ', ae
		db_session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500

	except Exception as e:
		print 'api_update_profile: Exception: ', e
		db_session.rollback()
		return jsonify(usrmsg=e), 500	

	print "api_update_profile: Something went wrong - Fell Through."
	print "here is the form object:"
	print str(form)

	return jsonify(usrmsg="Something went wrong."), 500




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
		prof_rate = request.values.get("edit_rate")
		oauth_stripe = request.values.get("edit_oauth_stripe")

		print "ht_validate_profile: prof rate is: ", prof_rate

		try:
			prof_rate = int(prof_rate)
			if (prof_rate > 10000):
				errors["edit_rate"] = "Let's keep it below $10,000 for now."
		except TypeError:
			errors["edit_rate"] = "Please keep it to a whole dollar amount (or zero)."

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

	if (form_page == 'payment' or form_page == 'full'):	
		bp.prof_rate = form.edit_rate.data		
		ba.stripe_cust = form.edit_oauth_stripe.data
		return True

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
	lesson_id = request.values.get('lesson_id', False)

	if (lesson_id):
		print "render_edit_portfolio_page(): Lesson ID:", lesson_id
		# warning.  dangerous. returning a LessonMap (which has same fields)
		portfolio = ht_get_serialized_images_for_lesson(lesson_id)
	else:
		print "render_edit_portfolio_page(): get all images for profile:"
		portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))





# This route initiates a new lesson
#@insprite_views.route('/lesson/new', methods=['GET', 'POST'])
#@req_authentication
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
#@insprite_views.route('/lesson/new/<lesson_id>', methods=['GET', 'POST'])
#@req_authentication
def render_new_lesson(lesson_id, form=None, errmsg=None):
	bp = Profile.get_by_uid(session['uid'])
	version = request.values.get("version")
	if (bp.availability == 0): return redirect('/dashboard')
	
	print "render_new_lesson: lesson_id is", lesson_id

	lesson = Lesson.get_by_id(lesson_id)
	lesson_state = lesson.get_state()
	print "render_new_lesson: lesson_state: ", lesson_state

	# Form will be none unless we are here after an unsuccessful form validation.
	if (form == None):
		print "render_new_lesson: no form submitted"


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
		form.lessonMaterialsProvided.data = lesson.lesson_materials_provided
		form.lessonMaterialsNeeded.data = lesson.lesson_materials_needed		
		form.lessonMakeLive.data = 'y'

		if (form.lessonRate.data <= 0):
			form.lessonRate.data = bp.prof_rate		

		if (lesson.lesson_flags < 2):
			form.lessonMakeLive.data = None

	else:
		# Submitted form didn't validate - repopulate from the submitted form instead of from the database.
		print "render_new_lesson: invalid form imported"
		

	return make_response(render_template('lesson_form.html', bp=bp, form=form, lesson_id=lesson_id, errmsg=errmsg, version=version, lesson_flags=lesson.lesson_flags))



# User is choosing to edit a lesson they previously saved - display the form
#@insprite_views.route('/lesson/edit/<lesson_id>', methods=['GET', 'POST'])
#@req_authentication
def render_edit_lesson(lesson_id, form=None, errmsg=None):
	bp = Profile.get_by_uid(session['uid'])
	if (bp.availability == 0): return redirect('/dashboard')
	
	print "render_edit_lesson: lesson_id is", lesson_id
	
	lesson = Lesson.get_by_id(lesson_id)
	lesson_state = lesson.get_state()
	print "render_edit_lesson: lesson_state: ", lesson_state


	if (bp.prof_id != lesson.lesson_profile): return redirect('/dashboard')

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
		form.lessonMaterialsProvided.data = lesson.lesson_materials_provided
		form.lessonMaterialsNeeded.data = lesson.lesson_materials_needed
		form.lessonAvail.data = lesson.lesson_avail
		form.lessonMakeLive.data = 'y'

		if (form.lessonRate.data <= 0):
			form.lessonRate.data = bp.prof_rate		

		# if (lesson_state == "INCOMPLETE" or lesson_state == "COMPLETED"):
		if (lesson.lesson_flags < 2):
			form.lessonMakeLive.data = None

	else:
		# Submitted form didn't validate - repopulate from the submitted form instead of from the database.
		print "render_edit_lesson: invalid form imported"
		form = session_form
		errmsg = session_errmsg
		

	# lessonUpdated = lesson.lesson_updated

	return make_response(render_template('lesson_form.html', bp=bp, form=form, lesson_id=lesson_id, errmsg=errmsg, version="edit", lesson_title=lesson.lesson_title, lesson_flags=lesson.lesson_flags))


# Update will run no matter which form (add or edit) was submitted. It's the same function for both form types (i.e. there is no "create").
#@insprite_views.route('/lesson/update/<lesson_id>', methods=['POST'])
#@req_authentication
def api_update_lesson(lesson_id):
	bp = Profile.get_by_uid(session['uid'])
	if (bp.availability == 0): return redirect('/dashboard')
	
	form = LessonForm(request.form)
	lesson = Lesson.get_by_id(lesson_id)

	if (bp.prof_id != lesson.lesson_profile): return redirect('/dashboard')	

	version = request.values.get("version")
	saved = request.values.get("saved")
	print "api_update_lesson: Version is", version
	print "api_update_lesson: Saved is", saved
	print 'api_update_lesson: Beginning lesson update ...'

	lesson_state = lesson.get_state()
	print "api_update_lesson: lesson_state: ", lesson_state

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

			print 'api_update_lesson: Redirecting to view lesson:', lesson_id
			return make_response(redirect("/lesson/"+lesson_id))

		else:
			print 'api_update_lesson: invalid POST', form.errors

	# If the form was saved, we don't need to validate - e.g. empty fields are ok.
	else:
		# User clicked the Save Button, not the submit button.
		if form:
			# We need to know if it was a valid form. If it was not, we will mark the lesson as incomplete.
			if form.validate_on_submit():
				print 'api_update_lesson: lesson was SAVED and it validated'
				if (lesson_state == "INCOMPLETE"):
					lesson.set_state(LESSON_STATE_COMPLETED)
				# If lesson was already submitted or available, do nothing
				
			else:
				print 'api_update_lesson: lesson was SAVED and it did NOT validate'
				if (lesson_state != "INCOMPLETE"):
					lesson.set_state(LESSON_STATE_INCOMPLETE)				
			
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
			lesson_flags = lesson.lesson_flags;
			print "api_update_lesson: Flags: ", lesson_flags
			return jsonify(valid="true", lesson_flags=lesson.lesson_flags)

	if (saved != "true"):

		print 'api_update_lesson: fell through - populating form data and returning.'
		print 'api_update_lesson: Here is the form data:', pprint(vars(form))

		errmsg = "Sorry, your lesson form has some missing or invalid info. Please check it and resubmit."
		session['form'] = form
		session['errmsg'] = errmsg

		return redirect(url_for("insprite.render_edit_lesson", lesson_id=lesson_id))


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

	if (lesson.lesson_materials_provided != form.lessonMaterialsProvided.data):
		print '\tUpdate lesson_materials_provided (' + str(lesson.lesson_materials_provided) + ') => ' + str(form.lessonMaterialsProvided.data)
		lesson.lesson_materials_provided = form.lessonMaterialsProvided.data
		update = True

	if (lesson.lesson_materials_needed != form.lessonMaterialsNeeded.data):
		print '\tUpdate lesson_materials_needed (' + str(lesson.lesson_materials_needed) + ') => ' + str(form.lessonMaterialsNeeded.data)
		lesson.lesson_materials_needed = form.lessonMaterialsNeeded.data
		update = True

	# If user pressed 'save', we already took care of state when validating.
	if (saved != "true"): 
		lesson_state = lesson.get_state()
		print "ht_update_lesson: Previous state: ", lesson_state

		if (lesson_state != "AVAILABLE"):
			lesson.set_state(LESSON_STATE_SUBMITTED)
			lesson.set_state(LESSON_STATE_AVAILABLE)
			update = True

	lesson_state = lesson.get_state()
	print "ht_update_lesson: Final state: ", lesson_state

	return update



# View the lesson page
#@insprite_views.route("/lesson/<lesson_id>", methods=['GET', 'POST'])
def render_lesson_page(lesson_id):
	avail = None
	bp = None

	if (lesson_id is None):
		return make_response(render_dashboard(usrmsg='Need to specify a lesson...'))

	if ('uid' in session):
		bp = Profile.get_by_uid(session['uid'])
		avail = Availability.get_by_prof_id(bp.prof_id)

	print "render_lesson_page(): Lesson ID:", lesson_id

	try:
		lesson = Lesson.get_by_id(lesson_id)
		portfolio = ht_get_serialized_images_for_lesson(lesson_id)
		mentor = Profile.get_by_prof_id(lesson.lesson_profile)
		reviews = htdb_get_composite_reviews(mentor)

		x = 0
		print "render_lesson_page(): getting industry"
		for x in range(len(Industry.industries)):
			if (x == int(lesson.lesson_industry)):
				industry = str(Industry.industries[x])
				print "render_lesson_page(): industry is ", industry
				break

		print "render_lesson_page(): mentor:", mentor
		print "render_lesson_page(): Lesson String:", pprint(lesson)
	except Exception as e:
		print 'render_lesson_page(): Exception Error:', e
		return redirect(url_for('insprite.render_dashboard', usrmsg='Sorry, We encountered an error loading that lesson.'))

	lesson_reviews = ht_filter_composite_reviews(reviews, 'REVIEWED', mentor, dump=False)
	show_reviews = ht_filter_composite_reviews(lesson_reviews, 'VISIBLE', None, dump=False)
	return make_response(render_template('lesson.html', bp=bp, lesson=lesson, portfolio=portfolio, mentor=mentor, industry=industry, reviews=show_reviews, avail=avail))




#@req_authentication
#@insprite_views.route("/lesson/<lesson_id>/images", methods=['GET', 'POST'])
def api_get_images_for_lesson(lesson_id):
	# move this to API.

	try:
		images = ht_get_serialized_images_for_lesson(lesson_id)
	except Exception as e:
		print "api_get_images_for_lesson: exception:", type(e), e
		raise e
	return jsonify(portfolio=images)


#@req_authentication
#@insprite_views.route("/lesson/<lesson_id>/retrieve", methods=['GET'])
def ht_api_retrieve_lesson(lesson_id):
	# move this to API.
	lesson = Lesson.get_by_id(lesson_id)
	# print "ht_api_retrieve_lesson: lesson: "+pprint(lesson)
	return jsonify(lesson=lesson.serialize)


def ht_get_serialized_images_for_lesson(lesson_id):
	# json_serialize all images assoicated with the lesson.
	images = LessonImageMap.get_images_for_lesson(lesson_id)
	return [img.serialize for img in images]


#@req_authentication
#@insprite_views.route("/portfolio/<operation>/", methods=['POST'])
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




#@req_authentication
#@insprite_views.route("/lesson/<lesson_id>/image/update", methods=['POST'])
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




@sc_users.route('/schedule', methods=['GET','POST'])
@req_authentication
def render_schedule_page():
	""" Schedule a new appointment appointment. """

	usrmsg = None
	form = ProposalForm(request.form)

	try:
		bp = Profile.get_by_uid(session.get('uid'))
		ba = Account.get_by_uid(session.get('uid'))
		#hack.
		mentor = bp #Profile.get_by_prof_id(request.values.get('mentor'))
		avail = Availability.get_by_prof_id(mentor.prof_id)	
		print 'render_schedule() mentor:', mentor


		form.process()

	except Exception as e:
		print type(e), e
		db_session.rollback()


	form.prop_mentor.data = mentor.prof_id
	print 'render_schedule(): using STRIPE: ', ht_server.config['STRIPE_SECRET']
	return make_response(render_template('schedule.html', bp=bp, mentor=mentor, form=form, STRIPE_PK=ht_server.config['STRIPE_PUBLIC'], buyer_email=ba.email, avail=avail, errmsg=usrmsg))


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




#@sc_views.route('/settings', methods=['GET', 'POST'])
#@req_authentication
def render_settings():
	""" Provides form for the user to change their settings."""
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	ba	= Account.get_by_uid(uid)

	errmsg = None
	insprite_msg = session.pop('messages', None)

	form = SettingsForm(request.form)

	email_unver = False
	if (ba.status == Account.USER_UNVERIFIED):
		email_unver = True

	print 'render_settings()', bp.prof_name, ' email unverified', email_unver

	form.set_input_email.data	= ba.email
	form.set_input_name.data	= ba.name
	nexturl = "/settings"
	if (request.values.get('nexturl') is not None):
		nexturl = request.values.get('nexturl')
	if (errmsg is None): errmsg = insprite_msg

	return make_response(render_template('settings.html', form=form, bp=bp, nexturl=nexturl, unverified_email=email_unver, errmsg=errmsg))



#@insprite_views.route('/settings/update', methods=['GET','POST'])
#@req_authentication
def ht_api_update_settings():
	# Process the edit settings form

	print "ht_api_update_settings: beginning update"

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	ba = Account.get_by_uid(uid)

	form = SettingsForm(request.form)

	try:
		if form.validate_on_submit():
			print 'ht_api_update_settings()\tvalid submit'
			update_acct = False		# requires current_pw_set, 					Sends email
			update_pass = None		# requires current_pw_set, valid new pw =>	Sends email
			update_mail = None
			update_name = None

			update_prop = None
			update_vnty = None
			update_fail = False

			if (form.set_input_name.data != ba.name):
				print 'ht_api_update_settings()\tupdate', str(ba.name) + " to " +  str(form.set_input_name.data)
				update_acct = True
				update_name = form.set_input_name.data

			if (form.set_input_newpass.data != ""):
				print 'ht_api_update_settings()\tupdate', str(ba.pwhash) + " to " +  str(form.set_input_newpass.data)
				update_acct = True
				update_pass = form.set_input_newpass.data

			if (ba.email != form.set_input_email.data):
				print 'ht_api_update_settings()\tupdate', str(ba.email) + " to " +  str(form.set_input_email.data)
				update_acct = True
				update_mail = form.set_input_email.data

			if (update_acct):
				print 'ht_api_update_settings()\tupdate account'
				pwd = form.set_input_curpass.data
				
				print 'ht_api_update_settings()\tnow call modify account()'
				(rc, errno) = modifyAccount(uid, pwd, new_pass=update_pass, new_mail=update_mail, new_name=update_name)
				print("ht_api_update_settings()\tmodify acct()  = " + str(rc) + ", errno = " + str(errno))
				
				if (rc == False):
					errmsg = str(errno)
					errmsg = error_sanitize(errmsg)
					form.set_input_curpass.data = ''
					form.set_input_newpass.data = ''
					form.set_input_verpass.data = ''
					print "update was false - errmsg:", errmsg
					errors = {}
					errors["set_input_curpass"] = "This didn't match the password in your account."

					return jsonify(usrmsg="Hmm... something went wrong.", errors=errors), 500
				else:
					print "ht_api_update_settings() Update should be complete"
					return jsonify(usrmsg="Settings updated"), 200
			else:
				# User didn't change anything.
				return jsonify(usrmsg="Cool... Nothing changed."), 200

			if (update_name):
				usrmsg = "Your account name has been updated."

			if (update_mail):
				# user changed email; for security, send confimration email to last email addr.
				ht_send_email_address_changed_confirmation(ba.email, form.set_input_email.data)
				usrmsg = "Your email has been updated."

			#change pass send email
			if (update_pass):
				send_passwd_change_email(ba.email)
				usrmsg = "Password successfully updated."

			print 'ht_api_update_settings() Finished Handling POST.'
		
		return jsonify(usrmsg='Sorry, there was a problem with the form.', errors=form.errors), 500
		
	except AttributeError as ae:
		print 'ht_api_update_settings: AttributeError: ', ae
		db_session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500

	except Exception as e:
		print 'ht_api_update_settings: Exception: ', e
		db_session.rollback()
		return jsonify(usrmsg=e), 500	


	print "ht_api_update_settings: Something went wrong - Fell Through."
	print "here is the form object:"
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
			image = ht_create_image(bp, image_data, comment="")

			if (lesson_id):
				print 'upload()\tlesson_id' + str(lesson_id)
				ht_map_image_to_lesson(image, lesson_id)

			if (update_profile_img):
				print 'upload()\tupdate profile img'
				bp.update_profile_image(image)

	return jsonify(tmp="/uploads/" + str(image.img_id))



@sc_users.route('/project/edit', methods=['GET', 'POST'])
@sc_users.route('/project/edit/<string:pid>', methods=['GET', 'POST'])
@req_authentication
def render_edit_project(pid=None):
	bp = Profile.get_by_uid(session['uid'])
	avail = Availability.get_by_prof_id(bp.prof_id)
	print "render_edit_project: profile[" + str(bp.prof_id) + "] project[" + str(pid) + "]"

	form = ProjectForm(request.form)
	# This project should be owned by the browsing user (not used right now)
	project = Project.get_by_proj_id(pid, bp)
	if (project):
		form.proj_id.data	= project.proj_id
		form.proj_name.data	= project.proj_name
		form.proj_addr.data = project.proj_addr
		form.proj_desc.data = project.proj_desc
#		form.proj_min.data	= project.proj_min
		form.proj_max.data	= project.proj_max
		form.proj_timeline.data	= project.timeline
		form.proj_contact.data	= project.contact

		print "render_edit_project: checking for scheduled time."
		schedule_call = Availability.get_project_scheduled_time(project.proj_id)
		if (schedule_call is not None):
				print "render_edit_project: setting values to ", str(schedule_call.avail_weekday), str(schedule_call.avail_start), str(schedule_call.avail_start)[:-3]
#				form.avail_day.data  = schedule_call.avail_weekday
#				form.avail_time.data = str(schedule_call.avail_start)[:-3]
	else:
		# set proj_id to 'new'
		form.proj_id.data	= 'new'

	return make_response(render_template('edit_project.html', title="- Edit Project", form=form, bp=bp))




@sc_users.route('/project/update', methods=['POST'])
@req_authentication
def api_update_project(usrmsg=None):
	# Process the edit profile form
	print "api_proj_update: start"

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	
	#proj_name     = TextField('Name', [validators.Required(), validators.length(min=1, max=40)])
	#proj_addr	= TextAreaField('Address', [validators.length(min=0, max=128)])
	#proj_desc	= TextAreaField('Description', [validators.Required(), validators.length(min=0, max=5000)])
	#proj_timeline	= TextField('Timeline')
	#proj_contact	= TextField('Contact')

	# validate all data manually. 
	form = ProjectForm(request.form)
#	print "api_proj_update: day", form.avail_day.data, form.avail_time.data

	try:
		errors = "CAH, no errors"
		if form.validate_on_submit():
			print "api_proj_update: valid submit"

			update = True;
			if (update):
				project = None
				print "api_proj_update: id = ", form.proj_id.data
				if form.proj_id is not 'new':
					# find project.
					project = Project.get_by_proj_id(form.proj_id.data)

				if (project == None):
					print "api_proj_update: create new project"
					project = Project(form.proj_name.data, uid)
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


				# in case of classic user fippery
#				if (project.proj_min > project.proj_max):
#					print 'Classic user fippery, SWAP!'
#					tmp = project.proj_min
#					project.proj_min = project.proj_max
#					project.proj_max = tmp

#				print "api_proj_update: set day/time = ", form.avail_day.data, form.avail_time.data
#				schedule_call = Availability.get_project_scheduled_time(project.proj_id)
#				print "api_proj_update: ", str(schedule_call)
#				if (schedule_call is None):
					# create new availabliity.
#					schedule_call = Availability(bp, project.proj_id)

#				print "api_proj_update: adding time/date"
#				schedule_call.avail_weekday = form.avail_day.data
#				schedule_call.avail_start =  form.avail_time.data
			


				print "api_proj_update: add"
				db_session.add(project)
#				db_session.add(schedule_call)
				db_session.commit()
				return jsonify(usrmsg="project updated", proj_id=project.proj_id), 200
			else:
				db_session.rollback()
				print "api_proj_update: update error"
				return jsonify(usrmsg="We messed something up, sorry", errors=form.errors), 500
		else:
			print 'api_proj_update: invalid POST', form.errors

		print "api_proj_update: invalid", 
		return jsonify(usrmsg='Sorry, some required info was missing or in an invalid format. Please check the form.', errors=form.errors), 500

	except AttributeError as ae:
		print "api_proj_update: exception", ae
		db_session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500
	except Exception as e:
		print type(e), e
		print "api_proj_update: exception", e
		db_session.rollback()
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
