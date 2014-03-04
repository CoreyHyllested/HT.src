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

from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import *
from server.infrastructure.tasks  import *
from server.ht_utils import *
from server import ht_server
from string import Template
from werkzeug.security       import generate_password_hash, check_password_hash
from werkzeug.datastructures import CallbackDict


def ht_bind_session(bp):
	""" preserve userid server-side """
	#http://stackoverflow.com/questions/817882/unique-session-id-in-python
	session['uid'] = bp.account
	trace('bound session sid[' + str(session.get_sid()) + '] uid[' + str(session['uid']) + ']')
	

def ht_get_profile(ba):
	"""return profile from account"""
	if (ba == None): return None

	profiles = Profile.query.filter_by(account=ba.userid).all()
	if (len(profiles) == 1): return profiles[0]
	return None



def ht_browsingprofile():
	#return Profile.query.filter_by(account=session['uid']).all()[0]
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



def create_account(name, email, passwd):
	challenge_hash = uuid.uuid4()

	try:
		hero = Account(name, email, generate_password_hash(passwd)).set_sec_question(str(challenge_hash))
		prof = Profile(name, hero.userid)
		db_session.add(hero)
		db_session.add(prof)
		db_session.commit()
	except Exception as e:
		trace(str(e))
		db_session.rollback()
		return None, False

	log_uevent(hero.userid, 'successfully created user')
	send_verification_email(email, uid=hero.userid, challenge_hash=challenge_hash)
	return (hero, prof)



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



def modifyProfile():
	pass

