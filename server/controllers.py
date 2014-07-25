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

import os, json, pickle, requests
import time, uuid, smtplib, urlparse, urllib, urllib2
import oauth2 as oauth
import OpenSSL, hashlib, base64
import pytz

from pprint import pprint as pp
from datetime import timedelta, datetime as dt
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import *
from server.infrastructure.tasks  import *
from server.ht_utils import *
from server import ht_server
from string import Template
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from werkzeug.security       import generate_password_hash, check_password_hash
from werkzeug.datastructures import CallbackDict


def ht_bind_session(bp):
	""" preserve userid server-side """
	#http://stackoverflow.com/questions/817882/unique-session-id-in-python
	session['uid'] = bp.account
	session['pid'] = bp.prof_id
	trace('bound session sid[' + str(session.get_sid()) + '] uid[' + str(session['uid']) + ']')


def ht_get_profile(ba):
	"""return profile from account"""
	if (ba == None): return None

	profiles = Profile.query.filter_by(account=ba.userid).all()
	if (len(profiles) == 1): return profiles[0]
	return None


def ht_browsingprofile():
	bp = Profile.query.filter_by(account=session.get('uid', 0)).all()
	if (len(bp) == 1): return bp[0]
	return None



def ht_authenticate_user(user_email, password):
	""" Returns authenticated account """

	trace("user_email = " + str(user_email) + ", password = " + str(password))
	accounts = Account.query.filter_by(email=(user_email)).all()
	if ((len(accounts) == 1) and check_password_hash(accounts[0].pwhash, password)):
		return accounts[0]

	if (len(accounts) > 1):
		trace("WTF.  Account len = " + len(accounts) + ". Cannot happen " + str(user_email))
	return None



def ht_authenticate_user_with_oa(oa_srvc, oa_data_raw):
	""" Returns authenticated account.  Unless one doesn't exist -- then create it. """

	print 'normalize oauth account data', oa_srvc
	oa_data = normalize_oa_account_data(oa_srvc, oa_data_raw)

	hero = None
	oauth_account = []

	try:
		print 'search Oauth for', oa_srvc, oa_data['oa_account']
		oauth_accounts = db_session.query(Oauth)																		\
								   .filter((Oauth.oa_service == oa_srvc) & (Oauth.oa_account == oa_data['oa_account']))	\
								   .all()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if len(oauth_accounts) == 1:
		print 'found oauth account for individual'
		oa_account = oauth_accounts[0]
		hero = Account.get_by_uid(oa_account.ht_account)
	else:
		print 'found ', len(oauth_accounts), 'so sign up user with this oauth account.'
		(hero, prof) = ht_create_account_with_oauth(oa_data['oa_name'], oa_data['oa_email'], oa_srvc, oa_data)
		#import_profile(prof, oa_srvc, oa_data)
	return hero



def ht_password_recovery(email):
	""" Password recovery
		returns a string provided to the user on success and failure.
	"""

	trace("Entering password recovery")
	account = Account.get_by_email(email)
	if (account is None):
		return "Invalid email."

	try:
		account.reset_security_question()
		db_session.add(account)
		db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()
		return str(e)

	ht_send_password_recovery_link(account)
	return "Password recovery email has been sent."




def ht_create_account(name, email, passwd):
	challenge_hash = uuid.uuid4()

	try:
		print 'create account and profile'
		account = Account(name, email, generate_password_hash(passwd)).set_sec_question(str(challenge_hash))
		profile = Profile(name, account.userid)
		db_session.add(account)
		db_session.add(profile)
		db_session.commit()
	except IntegrityError as ie:
		print type(ie), ie
		db_session.rollback()
		# raise --fail... user already exists
		# is this a third-party signup-merge?
			#-- if is is a merge.
		return (None, None)
	except Exception as e:
		print type(e), e
		db_session.rollback()
		return (None, None)

	ht_email_welcome_message(email, name, challenge_hash)
	return (account, profile)




def ht_create_account_with_oauth(name, email, oa_provider, oa_data):
	print 'ht_create_account_with_oauth: ', name, email, oa_provider
	(account, profile) = ht_create_account(name, email, str(uuid.uuid4()))

	if (account is None):
		print 'create_account failed. happens when same email address is used'
		print 'Right, now mention an account uses this email address.'
		print 'Eventually.. save oa variables; put session variable.  Redirect them to login again.  If they can.  Merge account.'
		return None, None

	try:
		print 'create oauth account'
		oa_user = Oauth(str(account.userid), oa_provider, oa_data['oa_account'], token=oa_data['oa_token'], secret=oa_data['oa_secret'], email=oa_data['oa_email'])
		db_session.add(oa_user)
		db_session.commit()
	except IntegrityError as ie:
		print type(ie), ie
		db_session.rollback()
		return None, None 
	except Exception as e:
		print type(e), e
		db_session.rollback()
		return None, None
	return (account , profile)




def import_profile(bp, oauth_provider, oauth_data):
	oa_data = normalize_oa_profile_data(oauth_provider, oauth_data)
	try:
		linked_id = oauth_data.get('id')
		summary   = oauth_data.get('summary')
		#recommend = oauth_data.get('recommendationsReceived')
		headline  = oauth_data.get('headline')
		industry  = oauth_data.get('industry')
		location  = oauth_data.get('location')

		print ("update profile")
		if (summary  is not None): bp.prof_bio = summary
		if (headline is not None): bp.headline = headline
		if (industry is not None): bp.industry = industry #linked_in_sanatize(INDUSTRY, industry)
		if (location['name'] is not None): bp.location = location['name'] #linked_in_sanatize(LOCATION, loc[name])

		print 'hero & prof created', bp.account, oauth_provider 
		oauth = Oauth(str(bp.account), oauth_provider, linked_id, token=session.get('linkedin_token'))

		db_session.add(bp)
		db_session.add(oauth)
		print ("committ update bp")
		db_session.commit()
	except IntegrityError as ie:
		print 'ah fuck, it failed', ie
		db_session.rollback()
	except Exception as e:
		print 'ah fuck, it failed other place', e
		db_session.rollback()




def normalize_oa_profile_data(provider, oa_data):
	data = {}
	if provider == OAUTH_LINKED:
		data['summary']	= oa_data.get('summary', None)
		data['headline'] = oa_data.get('headline', None)
		data['industry'] = oa_data.get('industry', None)
		data['location'] = oa_data.get('location', None)
		#recommend = oauth_data.get('recommendationsReceived')
	return data


def normalize_oa_account_data(provider, oa_data):
	data = {}
	print 'normalizing oauth data'
	if provider == OAUTH_LINKED:
		data['oa_service']	= provider
		data['oa_account']	= oa_data.get('id')
		data['oa_email']	= oa_data.get('CAH_email', None)
		data['oa_token']	= oa_data.get('CAH_token', None)
		data['oa_secret']	= oa_data.get('CAH_sec', None)
	elif provider == OAUTH_FACEBK:
		facebook = oa_data

		print 'normalize facebook data'
		data['oa_service']	= provider
		data['oa_account']	= facebook['id']
		data['oa_name']		= facebook['name']
		data['oa_email']	= facebook['email']
		data['oa_token']	= facebook['token']
		data['oa_secret']	= None
		data['oa_timezone'] = facebook.get('timezone', None)
		pp(data)

	return data




def htdb_get_composite_meetings(profile):
	hero = aliased(Profile, name='hero')
	user = aliased(Profile, name='user')

	meetings	= db_session.query(Proposal, user, hero)																\
							.filter(or_(Proposal.prop_user == profile.prof_id, Proposal.prop_hero == profile.prof_id))	\
							.join(user, user.prof_id == Proposal.prop_user)												\
							.join(hero, hero.prof_id == Proposal.prop_hero).all();

	map(lambda meeting: meeting_timedout(meeting), meetings)
	map(lambda meeting: display_partner_proposal(meeting, profile), meetings)
	return meetings




def meeting_timedout(meeting):
	proposal = meeting.Proposal

	if (proposal.prop_state != APPT_STATE_PROPOSED and proposal.prop_state != APPT_STATE_ACCEPTED):
		return

	utc_now = dt.now(timezone('UTC'))
	utcsoon = utc_now - timedelta(hours=20)

	try:
		prop_ts = proposal.prop_ts.astimezone(timezone('UTC'))
		prop_tf = proposal.prop_tf.astimezone(timezone('UTC'))
		prop_to	= prop_ts - timedelta(hours=20)
		print 'meeting_timeout()\t', proposal.prop_uuid, proposal.prop_desc[:20]
		print '\t\t\t' + prop_ts.strftime('%A, %b %d, %Y %H:%M %p %Z%z') + ' - ' + prop_tf.strftime('%A, %b %d, %Y %H:%M %p %Z%z') #in UTC -- not that get_prop_ts (that's local tz'd)

		if (proposal.prop_state == APPT_STATE_PROPOSED):
			print '\t\t\tPROPOSED...'
			if (prop_ts <= utcsoon):	# this is a bug.  Items that have passed are still showing up.
				print '\t\t\t\tTIMED-OUT\tOfficially timed out, change state immediately.'
				proposal.set_state(APPT_STATE_TIMEDOUT)
				db_session.add(proposal)
				db_session.commit()
			else:
				timeout = prop_to - utc_now
				print '\t\t\t\tSafe! proposal will timeout in ' + str(timeout.days) + ' days and ' + str(timeout.seconds/3600) + ' hours....' + ht_print_timedelta(timeout)
				setattr(meeting, 'timeout', ht_print_timedelta(timeout))
		elif (proposal.prop_state == APPT_STATE_ACCEPTED):
			print '\t\t\tACCEPTED...'
			if ((proposal.get_prop_tf() + timedelta(hours=4)) <= utc_now):
				print '\t\t\tSHOULD be FINISHED... now() > tf + 4 hrs.'
				print '\t\t\tFILTER Event out manually.  The events are working!!!'
				proposal.set_state(APPT_STATE_OCCURRED)	# Hack, see above

	except Exception as e:
		print type(e), e
		db_session.rollback()




def ht_get_active_meetings(profile):
	props = []
	appts = []
	rview = []

	meetings = htdb_get_composite_meetings(profile)
	props = filter(lambda p: (p.Proposal.prop_state == APPT_STATE_PROPOSED), meetings)
	appts = filter(lambda a: (a.Proposal.prop_state == APPT_STATE_ACCEPTED), meetings)
	rview = filter(lambda r: (r.Proposal.prop_state  & APPT_STATE_OCCURRED), meetings)
	print 'ht_get_active_meetings()\ttotal:', len(meetings), '\tproposals:', len(props), '\tappointments:', len(appts), '\treview:', len(rview)

	# flag 'uncaught' meetings (do this as an idempotent task). Flag them as timedout.  Change state to rejected.

	#for meeting in meetings:
	#	if (profile.prof_id == thread.UserMessage.msg_to):
	#		thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_from)
	#		mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_RECV_ARCHIVE) else inbox
	#	elif (profile.prof_id == thread.UserMessage.msg_from):
	#		thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_to)
	#		mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE) else inbox
	#	else:
	#		print 'Major error.  profile_id didn\'t match to or from'
	#		continue
	#	setattr(thread, 'thread_partner', thread_partner)
	#	mbox.append(thread)

	return (props, appts, rview)







def ht_get_unread_messages(profile):
	all_msgs	= htdb_get_composite_messages(profile)
	unread_msgs	= ht_filter_composite_messages(all_msgs, profile, filter_by='UNREAD')
	toProf_msgs = ht_filter_composite_messages(unread_msgs, profile, filter_by='RECEIVED', dump=False)
	return toProf_msgs


def ht_get_thread_messages(profile):
	all_msgs	= htdb_get_composite_messages(profile)
	msg_threads	= ht_filter_composite_messages(all_msgs, profile, filter_by='THREADS')
	return msg_threads



def htdb_get_composite_messages(profile):
	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')

	messages = db_session.query(UserMessage, msg_from, msg_to)																		\
							 .filter(or_(UserMessage.msg_to == profile.prof_id, UserMessage.msg_from == profile.prof_id))			\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)												\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();
	return messages



def ht_filter_composite_messages(message_set, profile, filter_by='RECEIVED', dump=False):
	messages = []
	if (filter_by == 'RECEIVED'):
		#print 'Searching message_set for messages received by ', profile.prof_name, profile.prof_id
		messages = filter(lambda msg: (msg.UserMessage.msg_to == profile.prof_id), message_set)
	if (filter_by == 'SENT'):
		#print 'Searching message_set for messages sent by', profile.prof_name, profile.prof_id
		messages = filter(lambda msg: (msg.UserMessage.msg_from == profile.prof_id), message_set)
	if (filter_by == 'UNREAD'):
		#print 'Searching message_set for messages marked as unread'
		messages = filter(lambda msg: ((msg.UserMessage.msg_flags & MSG_STATE_LASTMSG_READ) == 0), message_set)
	if (filter_by == 'THREADS'):
		#print 'Searching message_set for messages marked as unread'
		messages = filter(lambda msg: ((msg.UserMessage.msg_thread == msg.UserMessage.msg_id) == 0), message_set)

	if (dump):
		#print 'Original set',  len(message_set), "=>", len(messages)
		for msg in messages:
			print msg.msg_from.prof_name, 'sent', msg.msg_to.prof_name, 'about', msg.UserMessage.msg_subject, '\t', msg.UserMessage.msg_flags, '\t', msg.UserMessage.msg_thread
	return messages




def ht_get_active_author_reviews(profile):
	prof_reviews = htdb_get_composite_reviews(profile)
	active_reviews = ht_filter_composite_reviews(prof_reviews,	 filter_by='ACTIVE', profile=profile, dump=False)
	author_reviews = ht_filter_composite_reviews(active_reviews, filter_by='AUTHORED', profile=profile, dump=False)
	print 'ht_get_active_reviews() \ttotal:', len(prof_reviews), '\tactive:', len(active_reviews), '\tactive_authored:', len(author_reviews)
	return author_reviews



def htdb_get_composite_reviews(profile):
	hero = aliased(Profile, name='hero')
	user = aliased(Profile, name='user')
	appt = aliased(Proposal, name='appt')

	# COMPOSITE REVIEW OBJECT
	# OBJ.Review	# Review
	# OBJ.hero		# Profile of seller
	# OBJ.user		# Profile of buyer
	# OBJ.appt 		# Proposal object
	# OBJ.display	# <ptr> Profile of other person (not me)

	all_reviews = db_session.query(Review, appt, hero, user).distinct(Review.review_id)											\
								.filter(or_(Review.prof_reviewed == profile.prof_id, Review.prof_authored == profile.prof_id))	\
								.join(appt, appt.prop_uuid == Review.rev_appt)													\
								.join(user, user.prof_id == Review.prof_authored)												\
								.join(hero, hero.prof_id == Review.prof_reviewed).all();
	map(lambda review: display_review_partner(review, profile.prof_id), all_reviews)
	return all_reviews



def display_review_partner(r, prof_id):
	display_attr = (prof_id == r.Review.prof_reviewed) and r.user or r.hero
	setattr(r, 'display', display_attr)



def display_partner_proposal(meeting, profile):
	display_partner = (profile == meeting.hero) and meeting.user or meeting.hero
	setattr(meeting, 'display', display_partner)
	setattr(meeting, 'seller', (profile == meeting.hero))




def ht_filter_images(image_set, filter_by='VISIBLE', dump=False):
	images = []
	if (filter_by == 'VISIBLE'):
		images = filter(lambda img: (img.img_flags & IMG_STATE_VISIBLE), image_set)
	else:
		print '\t\t YOU DID NOT USE A VALID FILTER NAME'
	return images



def ht_filter_composite_reviews(review_set, filter_by='REVIEWED', profile=None, dump=False):
	reviews = []
	if (filter_by == 'REVIEWED'):
	#	print 'Searching review_set for reviews of', profile.prof_name, profile.prof_id
		reviews = filter(lambda r: (r.Review.prof_reviewed == profile.prof_id), review_set)
	elif (filter_by == 'AUTHORED'):
	#	print 'Searching review_set for reviews authored by', profile.prof_name, profile.prof_id
		reviews = filter(lambda r: (r.Review.prof_authored == profile.prof_id), review_set)
	elif (filter_by == 'VISIBLE'):
	#	print 'Searching review_set for reviews marked as visible'
		reviews = filter(lambda r: (r.Review.rev_status & REV_STATE_VISIBLE), review_set)
	elif (filter_by == 'ACTIVE'):
		reviews = filter(lambda r: (r.Review.rev_status & REV_STATE_CREATED), review_set)
	else:
		print '\t\t YOU SWUNG AND MISSED THE FILTER NAME'

	if (dump):
		print '\t\tfilter review_set by %s, by %s [%s]' % (filter_by, profile.prof_name, str(profile.prof_id)), '\tREVIEW SET: ', len(review_set), "=>", len(reviews)
		for r in reviews:
			# see htdb_get_composite_reviews() for object description.
			print '\t\t', r.user.prof_name, 'bought', r.hero.prof_name, 'on', r.Review.review_id, '\t', r.Review.rev_flags, '\t', r.Review.appt_score
	return reviews




def modifyAccount(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None):
	print uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca
	ba = Account.query.filter_by(userid=uid).all()[0]

	if (not check_password_hash(ba.pwhash, current_pw)):
		return False, "Password didn't match one on file"

	if (new_pass != None):
		print "updating hash", ba.pwhash, "to", new_pass, generate_password_hash(new_pass)
		ba.pwhash = generate_password_hash(new_pass)

	if (new_mail != None):
		print "update email", ba.email, "to", new_mail
		ba.email = new_mail

	try:
		db_session.add(ba)
		db_session.commit()
	except Exception as e:
		db_session.rollback()
		return False, e
	return True, True



def ht_assign_msg_threads_to_mbox(mbox_profile_id, msg_threads):
	inbox = []
	archive = []

	for thread in msg_threads:
		if (mbox_profile_id == thread.UserMessage.msg_to):
			thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_from)
			mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_RECV_ARCHIVE) else inbox
		elif (mbox_profile_id == thread.UserMessage.msg_from):
			thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_to)
			mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE) else inbox
		else:
			print 'Major error.  profile_id didn\'t match to or from'
			continue
		setattr(thread, 'thread_partner', thread_partner)
		mbox.append(thread)

	return (inbox, archive)




def ht_create_lesson(profile):
	lesson = None
	try:
		lesson = Lesson(profile.prof_id)
		print 'ht_create_lesson: creating lesson. Lesson data:',str(lesson)
		# lesson.set_state(LESSON_STATE_STARTED)
		db_session.add(lesson)
		db_session.commit()
	except IntegrityError as ie:
		print 'ht_create_lesson: ERROR ie:', ie
		db_session.rollback()
	except Exception as e:
		print 'ht_create_lesson: ERROR e:', type(e), e
		db_session.rollback()
	return lesson




def htdb_get_lesson_images(lesson_id):
	try:
		lesson_images	= db_session.query(LessonImageMap)								\
									.filter(LessonImageMap.map_lesson == lesson_id).all()
	except Exception as e:
		print type(e), e
	return lesson_images




def ht_get_active_lessons(profile):
	lessons = db_session.query(Lesson).filter(Lesson.lesson_profile == profile.prof_id).all();
	print "ht_get_active_lessons() \ttotal:", len(lessons)
	return lessons




def ht_email_verify(email, challengeHash, nexturl=None):
	# find account, if any, that matches the requested challengeHash
	accounts = Account.query.filter_by(sec_question=(challengeHash)).all()
	if (len(accounts) != 1 or accounts[0].email != email):
			session['messages'] = 'Verification code or email address, ' + str(email) + ', didn\'t match one on file.'
			return redirect(url_for('insprite.render_login'))

	try:
		print 'updating account'
		account = accounts[0]
		account.set_email(email)
		account.set_sec_question("")
		account.set_status(Account.USER_ACTIVE)

		db_session.add(account)
		db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	# bind session cookie to this user's profile
	profile = Profile.get_by_uid(account.userid)
	ht_bind_session(profile)
	if (nexturl is not None):
		# POSTED from jquery in /settings:verify_email not direct GET
		return make_response(jsonify(usrmsg="Account Updated."), 200)

	session['messages'] = 'Great! You\'ve verified your email'
	return redirect(url_for('insprite.render_dashboard'))





#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################

def ht_print_timedelta(td):
	if (td.days >= 9):
		return 'more than a week'
	if (td.days >= 6):
		return 'about a week'
	elif (td.days >=2):
		return str(td.days) + ' days'
	elif (td.days == 1):
		return 'one day'
	else:
		return str(td.seconds / 3600) + ' hours'


