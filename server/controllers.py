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

import os, json, pickle
import time, uuid, smtplib, urlparse, urllib, urllib2
import oauth2 as oauth
import OpenSSL, hashlib, base64
import requests

from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from models import Account, Profile
from redis  import Redis
from server import ht_server, models, db, linkedin
from server import emailer
from server.ht_utils import *
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

	profiles = models.Profile.query.filter_by(account=ba.userid).all()
	if (len(profiles) == 1): return profiles[0]
	return None



def ht_browsingprofile():
	#return models.Profile.query.filter_by(account=session['uid']).all()[0]
	return None

def send_email(toEmail, uid=None, verify=False, challenge_hash=None, passChange=None, emailChange=None, newEmail=None, recovery=None):

	fromEmail = "noreply@herotime.co"
    
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Nikola"
	msg['From'] = fromEmail
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"

    # Message body
    # text is plain-text email
    # html is the html version

	if verify:
		html = "Thank you for creating a HeroTime account. Click <a href=\"http://127.0.0.1:5000/signup/verify/" + str(challenge_hash) + "?email="+str(toEmail)+"&uid=" + str(uid) +"\">here</a> to verify your email."
		text = "Thank you for creating a HeroTime account. Go to http://127.0.0.1:5000/signup/verify/" + str(challenge_hash) + "?email="+str(toEmail)+"&uid="+str(uid) + " to verify your email."
	elif recovery:
		html = "Click <a href=\"http:127.0.0.1:5000/newpassword/" + str(challenge_hash) + "?email=" + str(toEmail) + "\">here</a> to recover your HeroTime password."
		text = "Go to http://127.0.0.1:5000/newpassword/" + str(challenge_hash) + "?email=" + str(toEmail) + " to recover your HeroTime password."
	elif passChange:
		html = "Your HeroTime password has been changed."
		text = html
	elif emailChange:
		html = "Your HeroTime email has been changed to " + newEmail + " If you did not make this change please let us know."
		text = html
	else:
		text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
		html = """\n
		<html>
			<head></head>
			<body>
				Welcome to HeroTime!<br>
				<br>
				Now go buy and sell time. Enjoy.
			</body>
		</html>
		"""

	# SendGrid login
	username = 'radnovic'
	password = "HeroTime"

	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	msg.attach(part1)
	msg.attach(part2)

	# Open a connection to the SendGrid mail server
	s = smtplib.SMTP('smtp.sendgrid.net', 587)

	s.login(username, password)

	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s.sendmail(fromEmail, toEmail, msg.as_string())

	s.quit()


def ht_authenticate_user(user_email, password):
	""" Returns authenticated account """

	trace("user_email = " + str(user_email) + ", password = " + str(password))
	accounts = models.Account.query.filter_by(email=(user_email)).all()
	if ((len(accounts) == 1) and check_password_hash(accounts[0].pwhash, password)):
		return accounts[0]

	if (len(accounts) > 1):
		trace("WTF.  Account len = " + len(accounts) + ". Cannot happen " + str(user_email))
	return None


def recovery(email):
	""" Password recovery process """
	trace("Entering password recovery")

	challenge_hash = uuid.uuid4()

	errmsg = None

	accounts = models.Account.query.filter_by(email=email).all()

	if (len(accounts) != 1):
		errmsg = "Invalid email."
	else:
		ba = accounts[0]
		ba.set_sec_question(str(challenge_hash))
		errmsg = "Password recovery email has been successfully sent."

		try:
			db.session.add(ba)
			db.session.commit()

		except Exception as e:
			trace(str(e))
			db.session.rollback()
			return None

		send_email(email, challenge_hash = challenge_hash, recovery=True)

	return errmsg


def create_account(name, email, passwd):
	challenge_hash = uuid.uuid4()

	try:
		hero = Account(name, email, generate_password_hash(passwd)).set_sec_question(str(challenge_hash))
		prof = Profile(name, hero.userid)
		db.session.add(hero)
		db.session.add(prof)
		db.session.commit()
	except Exception as e:
		trace(str(e))
		db.session.rollback()
		return None, False

	log_uevent(hero.userid, 'successfully created myself')
	mesg = Message("Welcome to HeroTime", sender="<HeroTime Accounts> accounts@herotime.co", recipients=[hero.email])
	mesg.html = "Click <a href=\"http://herotime.co/signup/verify/" + str(challenge_hash) + "?email="+str(hero.email)+"&uid=" + str(hero.userid) +"\">here</a> to get started."
	trace(mesg.html)
	#msg.text = "Click here to get started: \"http://127.0.0.1:5000/verify/" + str(challengeHash) + "?uid=" + str(userid) + "\""
	#emailer.send(msg)

	if (passwd != 'linkedin_oauth'):
		send_email(email, uid=hero.userid, verify=True, challenge_hash=challenge_hash)

	return (hero, prof)


def modifyAccount(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None):
	print uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca
	ba = models.Account.query.filter_by(userid=uid).all()[0]

	if (not check_password_hash(ba.pwhash, current_pw)):
		return False, "Password didn't match one on file"

	if (new_pass != None):
		print "updating hash", ba.pwhash, "to", new_pass, generate_password_hash(new_pass)
		ba.pwhash = generate_password_hash(new_pass)

	if (new_mail != None):
		print "update email", ba.email, "to", new_mail
		ba.email = new_mail

	try:
		db.session.add(ba)
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		return False, e
	return True, True


def modifyProfile():
	pass

