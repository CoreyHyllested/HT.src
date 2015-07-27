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

import os, re, json, pickle, requests, uuid
import smtplib, urlparse, urllib, urllib2
import time, pytz
import oauth2 as oauth
import OpenSSL, hashlib, base64

from pprint import pprint as pp
from datetime import timedelta, datetime as dt
from flask import request
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from server import sc_server
from server.infrastructure.tasks  import *
from server.infrastructure import errors
from server.models import *
from server.controllers.annotations import *
from server.controllers.forms		import *
from server.controllers.database	import *
from string import Template
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from werkzeug.security       import generate_password_hash, check_password_hash
from werkzeug.datastructures import CallbackDict



def bind_session(account, profile):
	""" preserve userid server-side """
	#http://stackoverflow.com/questions/817882/unique-session-id-in-python
	session['pid']	= profile.prof_id
	session['uid']	= account.userid
	session['role'] = account.role
	trace('bound session sid[' + str(session.get_sid()) + '] uid[' + str(session['uid']) + '] ' + str(session['role']))



def sc_authenticate_user(user_email, password):
	account = Account.get_by_email(user_email)
	if (account and check_password_hash(account.pwhash, str(password))):
		return account
	return None



def sc_authenticate_user_with_oa(oa_srvc, oa_data_raw):
	""" Returns authenticated account. Iff account doesn't exist -- create it. """

	print 'normalize oauth account data', oa_srvc
	oa_data = normalize_oa_account_data(oa_srvc, oa_data_raw)

	hero = None
	oauth_account = []

	try:
		print 'search Oauth for', oa_srvc, oa_data['oa_account']
		oauth_accounts = sc_server.database.session.query(Oauth)																		\
								   .filter((Oauth.oa_service == oa_srvc) & (Oauth.oa_account == oa_data['oa_account']))	\
								   .all()
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()

	if len(oauth_accounts) == 1:
		print 'found oauth account for individual'
		oa_account = oauth_accounts[0]
		hero = Account.get_by_uid(oa_account.ht_account)
	else:
		print 'found ', len(oauth_accounts), 'so sign up user with this oauth account.'
		(hero, prof) = sc_create_account_with_oauth(oa_data['oa_name'], oa_data['oa_email'], oa_srvc, oa_data)
		#import_profile(prof, oa_srvc, oa_data)
	return hero



def sc_password_recovery(email):
	""" Password recovery """
	trace("Entering password recovery")

	account = Account.get_by_email(email)
	if (account is None):
		raise NoEmailFound(email)

	try:
		account.reset_security_question()
		sc_server.database.session.add(account)
		sc_server.database.session.commit()
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()
		raise AccountError(str(e), email, 'An error occurred')
	sc_send_password_recovery_link(account)




def sc_create_account(name, email, passwd, phone=None, addr=None, ref_id=None, role=AccountRole.CUSTOMER):
	#geo_location = get_geolocation_from_ip()

	account = Account.get_by_email(email)
	if (account): raise AccountError(email, 'Email exists', user_msg='Email address already exists. Login instead?')

	try:
		print 'create account and profile', str(email), str(phone), str(addr) # str(geo_location.get('region_name')), str(geo_location.get('country_code'))
		account = Account(name, email, generate_password_hash(passwd), phone=phone, ref=ref_id, role=role)
		profile = Profile(name, account.userid, email, phone=phone) # geo_location)
		sc_server.database.session.add(account)
		sc_server.database.session.add(profile)
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print type(ie), ie
		sc_server.database.session.rollback()
		raise AccountError(email, str(ie), user_msg='An error occurred. Please try again.')
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()
		raise AccountError(email, str(e), user_msg='An error occurred. Please try again.')
	#finally:
	# if (account is None): raise AccountError.

	print 'bind-session'
	bind_session(account, profile)

	session.pop('ref_id', None)
	session.pop('ref_prof', None)
	gift_id = session.pop('gift_id', None)
	if (gift_id):
		try:
			# claim gift
			gift = GiftCertificate.get_by_giftid(gift_id)
			gift.gift_state = CertificateState.CLAIMED
			gift.gift_recipient_name = profile.prof_name
			gift.gift_recipient_prof = profile.prof_id
			gift.gift_dt_updated = dt.utcnow();
			sc_server.database.session.add(gift)
			sc_server.database.session.commit()
		except Exception as e:
			print type(e), e
			sc_server.database.session.rollback()

	print 'send-welcome-email'
	sc_email_welcome_message(email, name, account.sec_question)
	return profile




def sc_create_account_with_oauth(name, email, oa_provider, oa_data):
	print 'sc_create_account_with_oauth: ', name, email, oa_provider
	try:
		profile = sc_create_account(name, email, str(uuid.uuid4()))
	except AccountError as ae:
		print ae

	if (profile is None):
		print 'create_account failed. happens when same email address is used'
		print 'Right, now mention an account uses this email address.'
		print 'Eventually.. save oa variables; put session variable.  Redirect them to login again.  If they can.  Merge account.'
		return None, None

	try:
		print 'create oauth account'
		#get account from profile.... 
		oa_user = Oauth(str(account.userid), oa_provider, oa_data['oa_account'], token=oa_data['oa_token'], secret=oa_data['oa_secret'], email=oa_data['oa_email'])
		sc_server.database.session.add(oa_user)
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print type(ie), ie
		sc_server.database.session.rollback()
		return None, None 
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()
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

		sc_server.database.session.add(bp)
		sc_server.database.session.add(oauth)
		print ("committ update bp")
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print 'ah fuck, it failed', ie
		sc_server.database.session.rollback()
	except Exception as e:
		print 'ah fuck, it failed other place', e
		sc_server.database.session.rollback()




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




def meeting_timedout(composite_meeting, profile):
	meeting = composite_meeting.Meeting

	if ((not meeting.proposed()) and (not meeting.accepted())):
		return

	utc_now = dt.now(timezone('UTC'))
	utcsoon = utc_now - timedelta(hours=20)

	try:
		meet_ts = meeting.meet_ts.astimezone(timezone('UTC'))
		meet_tf = meeting.meet_tf.astimezone(timezone('UTC'))
		meet_to	= meet_ts - timedelta(hours=20)
		print 'meeting_timeout()\t', meeting.meet_id, meeting.meet_details[:20]
		print '\t\t\t' + meet_ts.strftime('%A, %b %d, %Y %H:%M %p %Z%z') + ' - ' + meet_tf.strftime('%A, %b %d, %Y %H:%M %p %Z%z') #in UTC -- not that get_prop_ts (that's local tz'd)

		if (meeting.meet_state == MeetingState.PROPOSED):
			print '\t\t\tPROPOSED Meeting...'
			if (meet_ts <= utcsoon):	# this is a bug.  Items that have passed are still showing up.
				print '\t\t\t\tTIMED-OUT\tOfficially timed out, change state immediately.'
				meeting.set_state(MeetingState.TIMEDOUT, profile)
				sc_server.database.session.add(meeting)
				sc_server.database.session.commit()
			else:
				timeout = meet_to - utc_now
				print '\t\t\t\tSafe! proposal will timeout in ' + str(timeout.days) + ' days and ' + str(timeout.seconds/3600) + ' hours....' + sc_print_timedelta(timeout)
				setattr(composite_meeting, 'timeout', sc_print_timedelta(timeout))
		elif (meeting.accepted()):
			print '\t\t\tACCEPTED meeting...'
			if ((meeting.get_meet_tf() + timedelta(hours=4)) <= utc_now):
				print '\t\t\tSHOULD be FINISHED... now() > tf + 4 hrs.'
				print '\t\t\tFILTER Event out manually.  The events are working!!!'
				meeting.set_state(MeetingState.OCCURRED)	# Hack, see above
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()






def ht_get_active_author_reviews(profile):
	prof_reviews = htdb_get_composite_reviews(profile)
	active_reviews = ht_filter_composite_reviews(prof_reviews,	 filter_by='ACTIVE', profile=profile, dump=False)
	author_reviews = ht_filter_composite_reviews(active_reviews, filter_by='AUTHORED', profile=profile, dump=False)
	print 'ht_get_active_reviews() \ttotal:', len(prof_reviews), '\tactive:', len(active_reviews), '\tactive_authored:', len(author_reviews)
	return author_reviews




def ht_create_search_object(hashmap, mentor_prof_id, filtered_results):
	mentor = hashmap[mentor_prof_id]
	filtered_results.append(mentor[0])

	lesson_hits = []
	total_score = mentor[0].prof_score

	# add lessons as appropriate
	for lesson in mentor:
		if (lesson.less_score > 0):
			total_score = total_score + lesson.less_score
			lesson_hits.append(lesson)

	lesson_hits.sort(key=lambda x: x.less_score, reverse=True)
	lesson_hits = lesson_hits[0:3]
	setattr(mentor[0], 'lesson_hits', lesson_hits)
	setattr(mentor[0], 'total_score', total_score)
	print '\tht_score_mentor: Profile[' + str(mentor[0].prof_score) + '|' + str(total_score) + ']\t'+ mentor[0].Profile.prof_name  + '\t' + str(len(lesson_hits))





def display_meeting_partner(composite_meeting, profile):
	display_partner = (profile == composite_meeting.hero) and composite_meeting.user or composite_meeting.hero
	setattr(composite_meeting, 'display', display_partner)
	setattr(composite_meeting, 'seller', (profile == composite_meeting.hero))
	setattr(composite_meeting, 'buyer', (profile == composite_meeting.user))



def ht_score_search_results(composite_lesson, keywords, hashmap):
	less_score = 0
	prof_score = 0

	for keyword in keywords:
		if (keyword in composite_lesson.Profile.prof_name.lower()):
#			print '\t\t', keyword, composite_lesson.Profile.prof_name.lower()
			prof_score = prof_score + 1
		if (keyword in composite_lesson.Profile.headline.lower()):
#			print '\t\t', keyword, composite_lesson.Profile.headline.lower()
			prof_score = prof_score + 1
		if (keyword in composite_lesson.Profile.prof_bio.lower()):
#			print '\t\t', keyword, composite_lesson.Profile.prof_bio.lower()
			prof_score = prof_score + 1
		if (keyword in composite_lesson.lesson.lesson_title.lower()):
#			print '\t\t', keyword, composite_lesson.lesson.lesson_title.lower()
			less_score = less_score + 1
		if (keyword in composite_lesson.lesson.lesson_description.lower()):
#			print '\t\t', keyword, composite_lesson.lesson.lesson_description.lower()
			less_score = less_score + 1

	setattr(composite_lesson, 'comp_score', (prof_score + less_score))
	setattr(composite_lesson, 'prof_score', prof_score)
	setattr(composite_lesson, 'less_score', less_score)

	if ((prof_score + less_score) > 0):
		# only add to map if at least one (profile/lesson) gets a hit.
		lesson_list = hashmap.get(composite_lesson.Profile.prof_id, [])
		lesson_list.append(composite_lesson)
		hashmap[composite_lesson.Profile.prof_id] = lesson_list

	print '\tht_score_lesson [' + str(less_score) + '|' + str(prof_score) + ']\t' + composite_lesson.Profile.prof_name, '\t', composite_lesson.lesson.lesson_title




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



def sc_update_account(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None, new_name=None):
	return modifyAccount(uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca, new_name)


def modifyAccount(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None, new_name=None):
	print uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca, new_name
	
	ba = Account.query.filter_by(userid=uid).all()[0]

	if (not check_password_hash(ba.pwhash, current_pw)):
		raise PasswordError(uid)

	if (new_pass != None):
		print "updating hash", ba.pwhash, "to", new_pass, generate_password_hash(new_pass)
		ba.pwhash = generate_password_hash(new_pass)

	if (new_mail != None):
		print "update email", ba.email, "to", new_mail
		ba.email = new_mail

	if (new_name != None):
		print "update name", ba.name, "to", new_name
		ba.name = new_name

	try:
		sc_server.database.session.add(ba)
		sc_server.database.session.commit()
	except Exception as e:
		sc_server.database.session.rollback()
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




def ht_create_avail_timeslot(profile):
	avail = None
	try:
		avail = Availability(profile)
		print 'ht_create_avail_timeslot: creating timeslot.'
		sc_server.database.session.add(avail)
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print 'ht_create_avail_timeslot: ERROR ie:', ie
		sc_server.database.session.rollback()
	except Exception as e:
		print 'ht_create_avail_timeslot: ERROR e:', type(e), e
		sc_server.database.session.rollback()
	return avail



def htdb_get_lesson_images(lesson_id):
	try:
		lesson_images = sc_server.database.session.query(LessonImageMap)				\
						.filter(LessonImageMap.map_lesson == lesson_id)	\
						.order_by(LessonImageMap.map_order).all()
	except Exception as e:
		print type(e), e
	return lesson_images




def sc_email_verify(email, challengeHash, nexturl=None):
	# find account, if any, that matches the requested challengeHash
	print "sc_email_verify: begin", email, nexturl, challengeHash

	accounts = Account.query.filter_by(sec_question=(challengeHash)).all()
	if (len(accounts) != 1 or accounts[0].email != email):
		print "sc_email_verify: error - challenge hash not found in accounts."
		session['messages'] = 'Verification code or email address, ' + str(email) + ', didn\'t match one on file.'
		return redirect(url_for('sc_ebody.render_login'))

	try:
		account = accounts[0]
		account.set_email(email)
		account.set_sec_question("")
		account.set_status(Account.USER_ACTIVE)

		sc_server.database.session.add(account)
		sc_server.database.session.commit()
		print 'sc_email_verify: account updated.'
	except Exception as e:
		print "sc_email_verify: Exception: ", type(e), e
		sc_server.database.session.rollback()

	# bind session cookie to this user's profile
	profile = Profile.get_by_uid(account.userid)
	bind_session(account, profile)
	if (nexturl is not None):
		# POSTED from jquery in /settings:verify_email not direct GET
		return make_response(jsonify(usrmsg="Email successfully verified."), 200)

	session['messages'] = 'Great! You\'ve verified your email'
	return redirect(url_for('sc_ebody.render_dashboard'))




#################################################################################
### DEPRECATED FUNCTIONS ########################################################
#################################################################################

@deprecated
def ht_create_account(name, email, passwd, ref_id):
	return sc_create_account(name, email, passwd, ref_id)

@deprecated
def ht_create_account_with_oauth(name, email, oa_provider, oa_data):
	return sc_create_account_with_oauth(name, email, oa_provider, oa_data)

@deprecated
def ht_get_unread_messages(profile):
	return sc_get_unread_messages(profile)

@deprecated
def ht_get_thread_messages(profile):
	return sc_get_thread_messages(profile)

@deprecated
def htdb_get_composite_messages(profile):
	return sc_get_composite_messages(profile)



#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################

def get_geolocation_from_ip(ip=None):
	if (ip is None): ip = request.remote_addr

	# find IPV4 addrs. http://www.shellhacks.com/en/RegEx-Find-IP-Addresses-in-a-File-Using-Grep
	pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
	if not re.match(pattern, ip):
		return dict()

	# this was hanging.... recheck to make sure it works
	ip = 'google.com'
	ip_geo_url= 'http://freegeoip.net/json/' + str(ip)
	print ip_geo_url
	return json.loads((urllib.urlopen(ip_geo_url)).read())


def sc_print_timedelta(td):
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


def get_day_string(day):
	d = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
	return d[day]


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
