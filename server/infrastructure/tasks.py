from __future__ import absolute_import
from datetime import datetime as dt
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import Account, Profile
from pprint import pprint as pp
import json, smtplib


@mngr.task
def getDBCorey(x):
	print ('in getDBCorey' + str(x))
	accounts = Account.query.filter_by(email=('corey.hyllested@gmail.com')).all()
	print ('accounts = ' + str(len(accounts)))
	if (len(accounts) == 1):
		print str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)
	print 'exit getDBCorey'
	return str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)



@mngr.task
def send_verification_email(toEmail, uid, challenge_hash):
	url  = 'https://herotime.co/signup/verify/' + str(challenge_hash) + "?email="+str(toEmail)+"&uid=" + str(uid)
	msg_text = "Thank you for creating a HeroTime account. Click <a href=\"" + str(url) + "\">here</a> to verify your email."
	msg_html = "Thank you for creating a HeroTime account. Go to " + str(url) + " to verify your email."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password Verification"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg) 


@mngr.task
def send_recovery_email(toEmail, challenge_hash):
	url = 'https://herotime.co/newpassword/' + str(challenge_hash) + "?email=" + str(toEmail)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = "Click <a href=\"" + url + "\">here</a> to recover your HeroTime password."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password Recovery"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)


@mngr.task
def send_welcome_email(toEmail):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """\n<html><head></head><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Welcome to HeroTime"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)


@mngr.task
def send_email_change_email(toEmail, newEmail):
	msg_html = "Your HeroTime email has been changed to " + newEmail + ". If you did not make this change please let us know."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Email address changed"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(toEmail, msg)


@mngr.task
def send_passwd_change_email(toEmail):
	msg_html = "Your HeroTime password has been updated."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password changed"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)


@mngr.task
def ht_send_email(toEmail, msg):
	# SendGrid login; TODO, move into config file.
	username = 'radnovic'
	password = "HeroTime"

	# Open a connection to the SendGrid mail server
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@herotime.co', toEmail, msg.as_string())
	s.quit()

@mngr.task
def capture_creditcard():
	return None  #not defined


@mngr.task
def getTS(jsonObj):
	pp(jsonObj)
	return str(dt.now())

@mngr.task
def chargeStripe(jsonObj):
	print 'inside chargeStripe()'
	return None

@mngr.task
def enable_reviews(jsonObj):
	#is this submitted after stripe?  
	print 'enable_reviews()'
	return None

@mngr.task
def disable_reviews(jsonObj):
	#30 days after enable, shut it down!
	print 'disable_reviews()'
	return None
	

if __name__ != "__main__":
	print 'CAH: load server.tasks for @mngr.task'
else:
	print "Whoa, this is main"
