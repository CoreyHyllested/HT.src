from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from email.header			import Header
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from pprint import pprint as pp
import json, smtplib
import stripe


def email_buyer_proposal_updated(prop, buyer_email, buyer_name, hero_name, hero_id):
	url = 'https://127.0.0.1:5000/profile?hero=' + str(hero_id)
	msg_html =	"Alright. We sent your proposal to <a href=\"" + str(url) + "\">" + hero_name + ".</a><br>"
	msg_html = msg_html + "The request was for " + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal to meet " + hero_name
	if (prop.prop_count > 1): msg_subject = msg_subject + "(updated)"

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(msg_subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(buyer_name, 'utf-8'), buyer_email)
	msg['From'] = "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(buyer_email, msg) 


def email_hero_proposal_updated(prop, hero_email, hero_name, buyer_name, buyer_id):
	print "Proposal to hero (" + str(prop.prop_uuid) + ") last touched by", str(prop.prop_from)

	url = 'https://127.0.0.1:5000/profile?hero=' + str(buyer_id)
	msg_html =	"Congrats. <br>";
	msg_html = msg_html + "<a href=\"" + url + "\">" 
	msg_html = msg_html + buyer_name 
	msg_html = msg_html + " </a> wants to buy your time.<br>"
	msg_html = msg_html + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	
	msg_subject = "Proposal to meet " + buyer_name  
	if (prop.prop_count > 1): msg_subject = msg_subject + " (updated)"

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(msg_subject, 'utf-8')
	msg['To']		= "\"%s\" <%s>" % (Header(hero_name, 'utf-8'), hero_email)
	msg['From']		= "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(hero_email, msg) 



@mngr.task
def send_verification_email(toEmail, uid, challenge_hash):
	url  = 'https://herotime.co/signup/verify/' + str(challenge_hash) + "?email="+str(toEmail)
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
def send_welcome_email(email_addr):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """\n<html><head></head><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Welcome to HeroTime"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = email_addr 
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(email_addr, msg)



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
def send_proposal_reject_emails(hero_email_addr, hero_name, buyer_email_addr, buyer_name, prop):
	hero_msg_html = "Hey, hero you can put away your cape and cowl for now..  You rejected proposal %s from USER." % (prop)
	hero_msg = MIMEMultipart('alternative')
	hero_msg['Subject']	= '%s'  % Header('HeroTime rejection notice.', 'utf-8')
	hero_msg['To']	 = "\"%s\" <%s>" % (Header(hero_name, 'utf-8'), hero_email_addr)
	hero_msg['From'] = "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_email_addr, hero_msg)

	buyer_msg_html = "Hey, keep your money.  Your hero is in another castle.  Your hero rejected your proposal %s." % (prop)
	buyer_msg = MIMEMultipart('alternative')
	buyer_msg['Subject']	= '%s'  % Header('HeroTime rejection notice.', 'utf-8')
	buyer_msg['To']			= "\"%s\" <%s>" % (Header(buyer_name, 'utf-8'), buyer_email_addr)
	buyer_msg['From']		= "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)



@mngr.task
def send_appt_emails(hero_email_addr, buyer_email_addr, appt):
	print 'sending appt emails@ ' + appt.ts_begin.strftime('%A, %b %d, %Y -- %H:%M %p')
	hero_msg_html = "Hey, Hero.  You have your cape and cowl.  You have an appointment on %s. was accepted." % (appt)
	hero_msg = MIMEMultipart('alternative')
	hero_msg['Subject'] = "HeroTime Appointment Confirmation."
	hero_msg['From'] = "noreply@herotime.co"
	hero_msg['To'] = hero_email_addr   #can be email name?
	hero_msg['fromname'] = "HeroTime"
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_email_addr, hero_msg)

	buyer_msg_html = "Congrats.  You have an appointment setup on %s. was accepted." % (appt)
	buyer_msg = MIMEMultipart('alternative')
	buyer_msg['Subject'] = "HeroTime Appointment Confirmation."
	buyer_msg['From'] = "noreply@herotime.co"
	buyer_msg['To'] = buyer_email_addr   #can be email name?
	buyer_msg['fromname'] = "HeroTime"
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)



@mngr.task
def send_prop_rejected_email(email_addr, proposal):
	msg_html = "Your HeroTime Proposal, %s, was rejected." % (proposal)

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "HeroTime Proposal Rejected"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = email_addr   #can be email name?
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	ht_send_email(email_addr, msg)



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
