from flask import render_template
from ..forms import LoginForm, NewAccountForm, ProfileForm, SettingsForm, NewPasswordForm
from ..forms import NTSForm, SearchForm, ReviewForm, RecoverPasswordForm, ProposalActionForm
from .helpers import *
from server.controllers import *
from server.ht_utils import *
from . import insprite_views



@insprite_views.route('/proposal/create', methods=['POST'])
@req_authentication
def ht_api_proposal_create():
	user_message = 'Interesting'

	try:
		print 'ht_api_proposal_create'
		proposal = ht_proposal_create(request.values, session['uid'])
		if (proposal is not None): user_message = 'Successfully created proposal'
	except Sanitized_Exception as se:
		user_message = se.get_sanitized_msg()
		return make_response(jsonify(usrmsg=user_message), se.httpRC())
	except Exception as e:
		print type(e), e
		return make_response(jsonify(usrmsg='Something bad'), 500)
	return make_response(jsonify(usrmsg=user_message, nexturl="/dashboard"), 200)




@insprite_views.route('/proposal/accept', methods=['POST'])
@req_authentication
def ht_api_proposal_accept():
	form = ProposalActionForm(request.form)
	pstr = "wants to %s proposal (%s); challenge_hash = %s" % (form.proposal_stat.data, form.proposal_id.data, form.proposal_challenge.data)
	log_uevent(session['uid'], pstr)

	if not form.validate_on_submit():
		msg = "invalid form: " + str(form.errors)
		log_uevent(session['uid'], msg) 
		return jsonify(usrmsg=msg), 400

	try:
		rc, msg = ht_proposal_accept(form.proposal_id.data, session['uid'])
		print rc, msg
	except Sanitized_Exception as se:
		return jsonify(usrmsg=se.get_sanitized_msg()), 500
	except Exception as e:
		print str(e)
		db_session.rollback()
		jsonify(usrmsg=str(e)), 500
	return make_response(redirect('/dashboard'))




@insprite_views.route('/proposal/negotiate', methods=['POST'])
@req_authentication
def ht_api_proposal_negotiate():
	#the_proposal = Proposal.get_by_id(form.proposal_id.data)
	#the_proposal.set_state(APPT_STATE_RESPONSE)
	#the_proposal.prop_count = the_proposal.prop_count + 1
	#the_proposal.prop_updated = dt.now()
	return jsonify('nooope'), 403 #notimplemented? 




@insprite_views.route('/proposal/reject', methods=['POST'])
@req_authentication
def ht_api_proposal_reject():
	form = ProposalActionForm(request.form)
	pstr = "wants to %s proposal (%s); challenge_hash = %s" % (form.proposal_stat.data, form.proposal_id.data, form.proposal_challenge.data)
	log_uevent(session['uid'], pstr)


	if not form.validate_on_submit():
		msg = "invalid form: " + str(form.errors)
		log_uevent(session['uid'], msg) 
		return jsonify(usrmsg=str(msg)), 504

	try:
		rc, msg = ht_proposal_reject(form.proposal_id.data, session['uid'])
	except NoProposalFound as npf:
		print rc, msg
		return jsonify(usrmsg="Weird, proposal doesn\'t exist"), 505
	except StateTransitionError as ste:
		db_session.rollback()
		print ste, ste.get_sanitized_msg()
		return jsonify(usrmsg=ste.get_sanitized_msg()), 500
	except DB_Error as ste:
		db_session.rollback()
		print ste
		return jsonify(usrmsg="Weird, some DB problem, try again"), 505
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify(usrmsg="Weird, some unknown issue: "+ str(e)), 505
	print rc, msg
	return jsonify(usrmsg="Proposal Deleted"), 200




@insprite_views.route('/appointment/cancel', methods=['POST'])
@dbg_enterexit
@req_authentication
def ht_api_appt_cancel():
	""" Cancels a logged in user's appointment. """

	uid = session['uid']
	print 'apptid = ', request.values.get('appt_id', 'Nothing found here, sir')

	try:
		the_proposal = Proposal.get_by_id(request.values.get('appt_id'))
		the_proposal.set_state(APPT_STATE_CANCELED)
		db_session.add(the_proposal)
		db_session.commit()
		print the_proposal

		#send emails notifying users.
		print "success, canceled appt"
	except DB_Error as dbe:
		print dbe
		db_session.rollback()
		return jsonify(usrmsg="Weird, some DB problem, try again"), 505
	except StateTransitionError as ste:
		print ste
		db_session.rollback()
		return jsonify(usrmsg=ste.get_sanitized_msg()), 500
	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg=nre), 400
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify(usrmsg='Bizarre, something failed'), 500

	return jsonify(usrmsg="succesfully canceled proposal"), 200






@req_authentication
@ht_server.route("/inbox/message/<msg_thread>", methods=['GET', 'POST'])
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




@insprite_views.route('/sendmsg', methods=['POST'])
@req_authentication
def ht_api_send_message():
	""" Send a user message. """

	uid = session['uid']

	try:
		bp = Profile.get_by_uid(session['uid'])

		msg_from = bp.prof_id
		msg_to	= request.values.get('hp')
		content	= request.values.get('msg')
		parent	= request.values.get('msg_parent')
		thread	= request.values.get('msg_thread')
		subject = request.values.get('subject')
		next	= request.values.get('next')

		print
		print "/sendmsg - MESSAGE DETAILS"
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
		email_user_to_user_message(bp, hp, subject, thread, message)
		return make_response(jsonify(usrmsg="Message sent.", next=next, valid="true"), 200)

	except DB_Error as dbe:
		print dbe
		db_session.rollback()
		return jsonify(usrmsg="Weird, some DB problem, try again", next=next, valid="true"), 505
	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg="Weird, couldn't find something", next=next, valid="true"), 505
	except Exception as e:
		print type(e)
		print e
		db_session.rollback()
		return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500



# TODO RENAME... 
@insprite_views.route("/postreview", methods=['GET','POST'])
@req_authentication
def ht_api_review():
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	print 'enter postreview'

	review_form = ReviewForm(request.form)
	print 'got form'

	print review_form
	print review_form.input_rating.data
	print review_form.input_review.data
	print review_form.review_id.data
	print review_form.score_comm.data
	print review_form.score_time.data

	if review_form.validate_on_submit():
		print 'form is valid'
		try:
			# add review to database
			the_review = Review.retreive_by_id(review_form.review_id.data)[0]
			the_review.appt_score = int(review_form.input_rating.data)
			the_review.generalcomments = review_form.input_review.data
			the_review.score_attr_comm = int(review_form.score_comm.data)
			the_review.score_attr_time = int(review_form.score_time.data)
			the_review.rev_status = the_review.rev_status | REV_STATE_VISIBLE
			rp = Profile.get_by_prof_id(the_review.prof_reviewed)	# reviewed  profile
			print 'form is updated'

			db_session.add(the_review)
			log_uevent(uid, "posting " + str(the_review))

			# update the reviewed profile's ratings, in the future, delay this
			# kick this out to another function.  
			reviews = Review.query.filter_by(prof_reviewed = rp.prof_id).all()
			sum_ratings = the_review.appt_score
			for old_review in reviews:
				sum_ratings += old_review.appt_score

			rp.updated = dt.now()
			rp.reviews = len(reviews) + 1
			rp.rating  = float(sum_ratings) / (len(reviews) + 1)
			log_uevent(rp.prof_id, "now has " + str(sum_ratings) + "points, and " + str(len(reviews) + 1) + " for a rating of " + str(rp.rating))
			db_session.add(rp)
			db_session.commit()
			print 'data has been posted'

			# flash review will be posted at end of daysleft
			# email alt user to know review was captured
			return make_response(redirect('/dashboard'))
		except Exception as e:
			print "had an exception with Review" + str(e)
			db_session.rollback()
			log_uevent(str(uid), "POST /review isn't valid " + str(review_form.errors))
			return jsonify(usrmsg='Data invalid')
	elif request.method == 'POST':
		print "POST New password isn't valid " + str(review_form.errors)
		return jsonify(usrmsg=str(review_form.errors))
	else:
		print "form wasn't posted"
		
	return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=bp, daysleft=str(28), form=review_form))

