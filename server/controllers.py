#################################################################################
# Copyright (C) 2013 - 2014 HeroTime, Inc.
# All Rights Reserved.
# 
# All information contained is the property of HeroTime, Inc.  Any intellectual 
# property about the design, implementation, processes, and interactions with 
# services may be protected by U.S. and Foreign Patents.  All intellectual 
# property contained within is covered by trade secret and copyright law.   
# 
# Dissemination or reproduction is strictly forbidden unless prior written 
# consent has been obtained from HeroTime, Inc.
#################################################################################

import os, json, pickle, requests
import time, uuid, smtplib, urlparse, urllib, urllib2
import oauth2 as oauth
import OpenSSL, hashlib, base64

from pprint import pprint as pp
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import *
from server.infrastructure.tasks  import *
from server.ht_utils import *
from server import ht_server, linkedin
from string import Template
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.exc import IntegrityError
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


#@deprecated use Account.get_by...
def ht_get_account(user_id=None):
	if (user_id == None): user_id = session.get('uid', 0)
	accounts = Account.query.filter_by(userid=user_id).all()
	if (len(accounts) == 1): return accounts[0]
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

	challenge_hash = uuid.uuid4()
	accounts = Account.query.filter_by(email=email).all()

	if (len(accounts) != 1):
		return "Not a valid email."

	ba = accounts[0]
	ba.set_sec_question(str(challenge_hash))
	usrmsg = "Password recovery email has been sent."

	try:
		db_session.add(ba)
		db_session.commit()
	except Exception as e:
		trace(str(e))
		db_session.rollback()
		return (str(e))

	send_recovery_email(email, challenge_hash)
	return usrmsg



def ht_create_account(name, email, passwd):
	challenge_hash = uuid.uuid4()

	try:
		print 'create account and profile'
		hero  = Account(name, email, generate_password_hash(passwd)).set_sec_question(str(challenge_hash))
		prof  = Profile(name, hero.userid)
		db_session.add(hero)
		db_session.add(prof)
		db_session.commit()

	except IntegrityError as ie:
		print ie
		db_session.rollback()
		# raise --fail... user already exists
		# is this a third-party signup-merge?
			#-- if is is a merge.
		return None, False
	except Exception as e:
		print e
		db_session.rollback()
		return None, False

	send_verification_email(email, uid=hero.userid, challenge_hash=challenge_hash)
	return (hero, prof)



def ht_create_account_with_oauth(name, email, oa_provider, oa_data):
	print 'ht_create_account_with_oauth: ', name, email, oa_provider
	(hero, prof) = ht_create_account(name, email, str(uuid.uuid4()))

	if (hero is None):
		print 'create_account failed. happens when same email address is used'
		print 'Right, now mention an account uses this email address.'
		print 'Eventually.. save oa variables; put session variable.  Redirect them to login again.  If they can.  Merge account.'
		return None, False

	try:
		print 'create oauth account'
		oa_user = Oauth(str(hero.userid), oa_provider, oa_data['oa_account'], token=oa_data['oa_token'], secret=oa_data['oa_secret'], email=oa_data['oa_email'])
		db_session.add(oa_user)
		db_session.commit()
	except IntegrityError as ie:
		print ie
		db_session.rollback()
		return None, False
	except Exception as e:
		print type(e)
		print e
		db_session.rollback()
		return None, False

	return (hero, prof)



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
			if (thread.UserMessage.msg_flags & MSG_STATE_RECV_ARCHIVE):
				archive.append(thread)
				print 'MsgThread_to_me, archived', (thread.UserMessage.msg_flags & MSG_STATE_RECV_ARCHIVE)
			else:
				inbox.append(thread)
				print 'MsgThread_to_me, inboxed'
		elif (mbox_profile_id == thread.UserMessage.msg_from):
			thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_to)
			#mbox = (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE) and archive or inbox
			if (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE):
				archive.append(thread)
				print 'MsgThread_from_me, archived', (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE)
			else:
				inbox.append(thread)
				print 'MsgThread_from_me, inboxed', (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE)
		else:
			print 'Major error.  profile_id didn\'t match to or from'
			continue
		setattr(thread, 'thread_partner', thread_partner)

	return (inbox, archive)


