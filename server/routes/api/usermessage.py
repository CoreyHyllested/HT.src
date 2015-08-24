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


from flask import render_template
from server import database
from server.models import *
from server.routes import api_routing as api 
from server.routes.helpers import *
from server.controllers import *
from server.sc_utils import *




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




@sc_authenticated
def get_message_thread(msg_thread):
	print 'get_message_thread: ', msg_thread
	bp = Profile.get_by_uid(session['uid'])

	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')
	thread_messages = []

	try:
		thread_messages = database.session.query(UserMessage, msg_from, msg_to)			\
							 .filter(UserMessage.msg_thread == msg_thread)				\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)	\
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
				database.session.add(msg.UserMessage)
		if (updated_messages > 0):
			print 'committing ' + str(updated_messages) + ' messages'
			database.session.commit()
	except Exception as e:
		print type(e), e
		database.session.rollback()

	thread_timestamp = msg_zero.UserMessage.msg_created

	map(lambda ptr: display_partner_message(ptr, bp.prof_id), thread_messages)
	return make_response(render_template('message.html', bp=bp, num_thread_messages=num_thread_messages, msg_thread_messages=thread_messages, msg_thread=msg_thread, subject=subject, thread_partner=thread_partner, thread_timestamp=thread_timestamp, archived=bool(thread_messages[0].UserMessage.archived(bp.prof_id))))




#@api.route('/sendmsg', methods=['POST'])
@sc_authenticated
def sc_api_send_message():
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

		print "sc_api_send_message() - MESSAGE DETAILS"
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
			database.session.add(msg_thread_leader)

		message = UserMessage(msg_to, bp.prof_id, content, subject=subject, thread=thread, parent=parent)
		database.session.add(message)
		database.session.commit()

		hp = Profile.get_by_prof_id(msg_to)
		ht_send_peer_message(bp, hp, subject, thread, message)
		return make_response(jsonify(usrmsg="Message sent.", next=next, valid="true"), 200)

	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg="Weird, couldn't find something", next=next, valid="true"), 505
	except Exception as e:
		print type(e), e
		database.session.rollback()
		return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500

