#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents. All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from . import sc_ebody, sc_users
from flask import render_template
from ..forms import ReviewForm
from .helpers import *
from server.controllers import *
from server.sc_utils import *
from server.models import *



@sc_users.route('/review/request', methods=['POST'])
def api_review_request():
	print 'api_review_request(): enter'
	email = request.values.get('invite_emails', None)
	print 'email =', email
	resp_code	= 200
	resp_mesg	= 'Created'

	# if email already exists... send back 200 (scroll-to and flash border?)
	template	= render_template('fragment_request.html', email=email, date=dt.utcnow())
	return make_response(jsonify(sc_msg=resp_mesg, embed=template), resp_code)



@sc_ebody.route('/purchase/create', methods=['POST'])
def sc_api_purchase_create():
	print 'sc_api_purchase_create(): enter'
	resp_message = 'Purchase created'
	resp_code = 200

	try:
		recipient = {};
		purchaser = {};
		stripe = {};

		# There should be a better way of getting this data, right?
		recipient['name'] = request.values.get('recipient[name]')
		recipient['addr'] = request.values.get('recipient[addr]')
		recipient['mail'] = request.values.get('recipient[mail]')
		recipient['cell'] = request.values.get('recipient[cell]')
		recipient['note'] = request.values.get('recipient[note]')
		print recipient['name'], recipient['addr'], recipient['mail'], recipient['cell'], recipient['note']

		purchaser['name'] = request.values.get('purchaser[name]')
		purchaser['cost'] = request.values.get('purchaser[cost]')
		purchaser['mail'] = request.values.get('stripe_mail')
		print purchaser['name'], purchaser['mail'], purchaser['cost']

		stripe['token'] = request.values.get('stripe_tokn')				# used to charge, *I think this points at CC*
		#stripe['amountpaid'] = request.values.get('purchaser[paid]')		# Should be grabbed from stripe somewhere.
		stripe['creditcard'] = request.values.get('stripe_card')	# save to sc customer
		stripe['customerid'] = request.values.get('stripe_cust')	# stripe customer id
		stripe['transaction'] = request.values.get('stripe_trnx')
		stripe['fingerprint'] = request.values.get('stripe_fngr')
		print 'sc_api_purchase_gift: stripe::', stripe['token'], stripe['creditcard'], stripe['transaction']

		for k in request.values:
			pass
			#print k, values[k]

		print 'sc_api_purchase_create(): purchase_gift'
		sc_purchase_gift(recipient, purchaser, stripe, session.get('uid'))
	except SanitizedException as se:
		print 'sc_api_purchase_create() sanitized messages',  se.sanitized_msg()
		return se.api_response(request.method)

	print 'sc_api_purchase_create(): response'
	return make_response(jsonify(usrmsg=resp_message, nexturl="/dashboard"), resp_code)




def sc_purchase_gift(recipient, purchaser, stripe, uid):
	""" Create a Purchase (gift). """

	print 'sc_purchase_gift: enter()'
	try:
		# check if recipient, purchaser are users...
		#	recipient_prof = Column(String(40), ForeignKey('profile.prof_id'))			# THE PROFILE who can make a decision. (to accept, etc)

#		print 'sc_purchase_gift: (' + str(prof_name) + ', ' + str(stripe_cust) + ')'
		gift = GiftCertificate(recipient, purchaser, stripe)
		db_session.add(gift)
		db_session.commit()
		print "sc_purchase_gift: successfully added gift"

		print "sc_purchase_gift: now charge and capture"
		gift.capture()
	except Exception as e:
		# IntegrityError, from commit()
		# SanitizedException(None), from Meeting.init()
		print type(e), e
		db_session.rollback()
		ht_sanitize_error(e)
	print "sc_purchase_gift: sending notifications"
	# add code to send notification.
	#ht_send_meeting_proposed_notifications(meeting, ha, hp, ba, bp)



#@insprite_views.route('/meeting/accept', methods=['GET','POST'])
@sc_authenticated
def ht_api_meeting_accept():
	meet_id = request.values.get('meet_id', None)
	print 'ht_api_meeting_accept(' + meet_id + ')\tenter'
	resp_code = 200
	resp_message = 'Proposed meeting accepted.'

	try:
		profile = Profile.get_by_uid(session['uid'])
		ht_meeting_accept(meet_id, profile)
		print 'ht_api_meeting_accept\t success'
	except SanitizedException as se:
		print "ht_api_meeting_accept: sanitized exception", se
		return se.api_response(request.method)

	if (request.method == 'GET'):
		# user accepted proposal from an email.
		if (resp_code == 200): session['messages'] = resp_message
	return make_response(redirect(url_for('insprite.render_dashboard')))




#@insprite_views.route('/meeting/negotiate', methods=['POST'])
@sc_authenticated
def ht_api_meeting_negotiate():
	#meeting = Meeting.get_by_id(form.proposal_id.data)
	#meeting.set_state(MeetingState.NEGOTIATE)
	#meeting.prop_count = meeting.prop_count + 1
	return jsonify(usrmsg='nooope'), 404 #notimplemented?




#@insprite_views.route('/meeting/reject', methods=['GET', 'POST'])
@sc_authenticated
def ht_api_meeting_reject():
	# cannot use form to validate inputs. do manually
	meet_id = request.values.get('meet_id', None)
	resp_code = 200
	resp_message = 'Proposed meeting rejected.'

	try:
		profile = Profile.get_by_uid(session['uid'])
		ht_meeting_reject(meet_id, profile)
		print 'ht_api_meeting_reject()\tsuccess'
	except SanitizedException as se:
		print "ht_api_proposal_reject(): sanitized exception", se
		return se.api_response(request.method)

	if (request.method == 'GET'):
		# from email, send to /dashboard.
		session['messages'] = resp_message
		return make_response(redirect(url_for('insprite.render_dashboard')))
	return jsonify(usrmsg=resp_message), resp_code




#@insprite_views.route('/meeting/cancel', methods=['GET', 'POST'])
@sc_authenticated
def ht_api_meeting_cancel():
	# cannot use form to validate inputs. do manually
	meet_id = request.values.get('meet_id', None)
	resp_code = 200
	resp_message = 'Canceled meeting.'

	try:
		bp = Profile.get_by_uid(session['uid'])
		ht_meeting_cancel(meet_id, bp)
	except SanitizedException as se:
		print "ht_api_meeting_cancel()\t EXCEPTION", se
		return se.api_response(request.method)
	return jsonify(usrmsg=resp_message), resp_code




#@insprite_views.route("/inbox/message/<msg_thread>", methods=['GET', 'POST'])
@sc_authenticated
def ht_api_get_message_thread(msg_thread):
	print 'ht_api_get_message_thread: ', msg_thread
	bp = Profile.get_by_uid(session['uid'])

	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')
	thread_messages = []

	try:
		thread_messages = db_session.query(UserMessage, msg_from, msg_to)					\
							 .filter(UserMessage.msg_thread == msg_thread)					\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)		\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();
		print "number of thread_messages", len(thread_messages)
	except Exception as e:
		print e

	msg_zero = filter(lambda msg: (msg.UserMessage.msg_id == msg.UserMessage.msg_thread), thread_messages)[0]
	num_thread_messages = len(thread_messages)

	if (num_thread_messages > 0):
		if (bp.prof_id == msg_zero.UserMessage.msg_from):
			thread_partner_id = msg_zero.UserMessage.msg_to
		else:
			thread_partner_id = msg_zero.UserMessage.msg_from

		thread_partner = Profile.get_by_prof_id(thread_partner_id)
			
		subject = msg_zero.UserMessage.msg_subject
		
		if ((msg_zero.msg_from != bp) and (msg_zero.msg_to != bp)):
			print 'user doesn\'t have access'
			thread_messages = []

	try:
		updated_messages = 0
		for msg in thread_messages:
			if (bp.prof_id == msg.UserMessage.msg_to and msg.UserMessage.msg_opened == None):
				print 'user message never opened before'
				updated_messages = updated_messages + 1
				msg.UserMessage.msg_opened = dt.utcnow();
				msg.UserMessage.msg_flags = (msg.UserMessage.msg_flags | MSG_STATE_LASTMSG_READ)
				db_session.add(msg.UserMessage)
		if (updated_messages > 0):
			print 'committing ' + str(updated_messages) + ' messages'
			db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	thread_timestamp = msg_zero.UserMessage.msg_created

	map(lambda ptr: display_partner_message(ptr, bp.prof_id), thread_messages)
	return make_response(render_template('message.html', bp=bp, num_thread_messages=num_thread_messages, msg_thread_messages=thread_messages, msg_thread=msg_thread, subject=subject, thread_partner=thread_partner, thread_timestamp=thread_timestamp, archived=bool(thread_messages[0].UserMessage.archived(bp.prof_id))))




#@insprite_views.route('/sendmsg', methods=['POST'])
@sc_authenticated
def ht_api_send_message():
	""" Send a user message. """

	try:
		bp = Profile.get_by_uid(session['uid'])

		msg_from = bp.prof_id
		msg_to	= request.values.get('hp')
		content	= request.values.get('msg')
		parent	= request.values.get('msg_parent')
		thread	= request.values.get('msg_thread')
		subject = request.values.get('subject')
		next	= request.values.get('next')

		print "ht_api_send_message() - MESSAGE DETAILS"
		print 'message from ' + bp.prof_name
		print 'message to ' + msg_to
		print 'subject=', subject
		print 'parent=', parent
		print 'thread=', thread
		print 'next=', next

		domAction = None

		if (parent):
			# print ('get thread leader', thread)
			msg_thread_leader = UserMessage.get_by_msg_id(thread)
			#if (msg_thread_leader.msg_to != bp.prof_id or msg_thread_leader.msg_from != bp.prof_id):
				# prevent active tampering.
				#return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500

			msg_to = (msg_thread_leader.msg_to != bp.prof_id) and msg_thread_leader.msg_to or msg_thread_leader.msg_from

			# set thread updated flag and clear archive flags for both users.
			archive_flags = (MSG_STATE_RECV_ARCHIVE | MSG_STATE_SEND_ARCHIVE)
			msg_thread_leader.msg_flags = msg_thread_leader.msg_flags | MSG_STATE_THRD_UPDATED
			msg_thread_leader.msg_flags = msg_thread_leader.msg_flags & ~(archive_flags)
			db_session.add(msg_thread_leader)

		message = UserMessage(msg_to, bp.prof_id, content, subject=subject, thread=thread, parent=parent)
		db_session.add(message)
		db_session.commit()

		hp = Profile.get_by_prof_id(msg_to)
		ht_send_peer_message(bp, hp, subject, thread, message)
		return make_response(jsonify(usrmsg="Message sent.", next=next, valid="true"), 200)

	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg="Weird, couldn't find something", next=next, valid="true"), 505
	except Exception as e:
		print type(e), e
		db_session.rollback()
		return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500




#@insprite_views.route("/review/create/<review_id>", methods=['GET','POST'])
@sc_authenticated
def ht_api_review_create(review_id):
	msg = None
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])

	review_form = ReviewForm(request.form)
	print review_form.review_id.data
	print review_form.input_review.data
	print review_form.input_rating.data  #score_meet.data
	print review_form.score_comm.data
	print review_form.score_time.data

	# check review for validity.
	if review_form.validate_on_submit():
		print 'ht_api_review_create() form is valid'
		try:
			# get review from database, modify and update review.
			review = Review.get_by_id(review_form.review_id.data)
			review.appt_score = int(review_form.input_rating.data)
			review.generalcomments = review_form.input_review.data
			review.score_attr_comm = int(review_form.score_comm.data)
			review.score_attr_time = int(review_form.score_time.data)
			review.set_state(REV_STATE_FINSHED)
			print 'ht_api_review_create() form is updated'

			db_session.add(review)
			db_session.commit()
			#log_uevent(uid, "posting " + str(review))

			print 'ht_api_review_create() data has been posted'
			profile_reviewed = Profile.get_by_prof_id(review.prof_reviewed)		# reviewed profile
			ht_post_review(review)

			# thank user for submitting review & making the world a better place
			return jsonify(usrmsg='Thanks for submitting review. It will be posted shortly'), 200
		except Exception as e:
			print "ht_api_review_create().  Exception...\n", type(e), e
			db_session.rollback()
			raise e
	elif request.method == 'POST':
		print "ht_api_review_create()  POST isn't valid " + str(review_form.errors)
		msg = {}
		for error in review_form.errors:
			if (error == 'input_rating'): key = "Overall Value option"
			elif (error == 'score_comm'): key = "Communication option"
			elif (error == 'score_time'):	key = "Promptness option"
			elif (error == 'input_review'):	key = "Your Experience"
			msg[key] = review_form.errors[error][0].decode().lower()
		return jsonify(usrmsg=msg), 400
	else:
		print "ht_api_review_create()  form wasn't posted"
		
	return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=profile_reviewed, form=review_form, usrmsg=msg))





################################################################################
### API HELPER FUNCTIONS. ######################################################
################################################################################


def ht_profile_update_reviews(profile):
	print 'ht_profile_update_reviews, updating profile,', profile.prof_name, profile.prof_id, '...\n'

	try:
		all_visible_reviews = Review.query.filter_by(prof_reviewed = profile.prof_id).filter_by(rev_status = REV_STATE_VISIBLE).all()

		profile_rating = 0
		print '\t', 'total of', len(all_visible_reviews)
		for review in all_visible_reviews:
			profile_rating += review.appt_score
			print '\t', review, ' quality points = ', profile_rating

		profile.updated = dt.now()
		profile.reviews = len(all_visible_reviews)
		profile.rating  = float(profile_rating) / len(all_visible_reviews)

		print(profile.prof_id, "now has " + str(profile_rating) + " points, and " + str(len(all_visible_reviews)) + " for a rating of " + str(profile.rating)) #log_uevent
		db_session.add(profile)
		db_session.commit()
	except Exception as e:
		print 'updating profile,', profile.prof_id, '...\n', type(e), e
		db_session.rollback()
		raise e




def ht_post_review(review):
	""" Check if sibling-review is posted; if so make them both reviews visible. """
	meeting = Meeting.get_by_id(review.rev_appt)
	rev_sellr_id = meeting.review_sellr		# review mentor
	rev_buyer_id = meeting.review_buyer		# review mentee

	review_twin_id = (review.review_id == rev_sellr_id) and rev_buyer_id or rev_sellr_id
	review_twin = Review.get_by_id(review_twin_id)
	print 'ht_post_review(): ' + str(review.review_id) + '\treview_twin: ' + str(review_twin_id)
	if (review_twin is None): raise NoReviewFound(review_twin_id) 

	if (not review_twin.completed()):
		print 'ht_posting_review_update_proposal():  just this review is available.'
		return

	try:
		print 'ht_posting_review_update_proposal():  make both reviews live'
		review.set_state(REV_STATE_VISIBLE)
		review.updated = dt.utcnow()
		review_twin.set_state(REV_STATE_VISIBLE)
		review_twin.updated = dt.utcnow()

		print 'ht_posting_review_update_proposal():  commit to DB'
		db_session.add(review)
		db_session.add(review_twin)
	except Exception as e:
		print 'ht_posting_review_update_proposal(): ', type(e), e
		db_session.rollback()

	print 'ht_posting_review_update_proposal(): update profiles'
	profile_sellr = Profile.get_by_prof_id(review.prof_authored)		# authored profile
	profile_buyer = Profile.get_by_prof_id(review.prof_reviewed)		# reviewed profile
	print 'ht_posting_review_update_proposal(): profile', profile_sellr.prof_name
	print 'ht_posting_review_update_proposal(): profile', profile_buyer.prof_name
	ht_profile_update_reviews(profile_sellr)
	ht_profile_update_reviews(profile_buyer)



