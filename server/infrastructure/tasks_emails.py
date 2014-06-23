from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from email.header			import Header
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
from pprint import pprint as pp
import json, smtplib
import stripe


def email_user_to_user_message(send_prof, recv_prof, msg_subject, thread, message):
	print 'email_user_to_user_message'
	try:
		print 'get recvr email'
		recv_account = Account.get_by_uid(recv_prof.account)
		send_account = Account.get_by_uid(send_prof.account)
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (message.msg_flags & MSG_STATE_THRD_UPDATED):
		msg_subject = msg_subject + " (updated)"

	# create email body
	msg_html = '<p>' + str(message.msg_content) + '</p>'
	msg_to_recvr_html = '<p>From ' + send_prof.prof_name + ':</p>' + msg_html
	msg_to_sendr_html = '<p>Sent to ' + recv_prof.prof_name + '</p>' + msg_html

	msg_to_recvr = create_msg(msg_subject, recv_account.email, recv_prof.prof_name, 'messages-'+str(message.msg_thread)+'@herotime.co', u'HeroTime Messages')
	msg_to_recvr.attach(MIMEText(msg_to_recvr_html, 'html', 'UTF-8'))
	ht_send_email(recv_account.email, msg_to_recvr)

	msg_to_sendr = create_msg(msg_subject, send_account.email, send_prof.prof_name, 'messages-'+str(message.msg_thread)+'@herotime.co', u'HeroTime Messages')
	msg_to_sendr.attach(MIMEText(msg_to_sendr_html, 'html', 'UTF-8'))
	ht_send_email(send_account.email, msg_to_sendr)



def email_user_proposal_updated(prop, buyer_email, buyer_name, hero_name, hero_id):
	url = 'https://herotime.co/profile?hero=' + str(hero_id)
	msg_html =	"Alright. We sent your proposal to <a href=\"" + str(url) + "\">" + hero_name + ".</a><br>"
	msg_html = msg_html + "The request was for " + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal to meet " + hero_name
	if (prop.prop_count > 1): msg_subject = msg_subject + "(updated)"

	msg = create_msg(msg_subject, buyer_email, buyer_name, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(buyer_email, msg) 




def email_hero_proposal_updated(prop, hero_email, hero_name, buyer_name, buyer_id):
	print "Proposal to hero (" + str(prop.prop_uuid) + ") last touched by", str(prop.prop_from)

	url = 'https://herotime.co/profile?hero=' + str(buyer_id)
	msg_html =	"Congrats. <br>";
	msg_html = msg_html + "<a href=\"" + url + "\">" 
	msg_html = msg_html + buyer_name 
	msg_html = msg_html + " </a> wants to buy your time.<br>"
	msg_html = msg_html + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal to meet " + buyer_name  
	if (prop.prop_count > 1): msg_subject = msg_subject + " (updated)"

	msg = create_msg(msg_subject, hero_email, hero_name, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(hero_email, msg) 



@mngr.task
def send_verification_email(toEmail, uid, challenge_hash):
	url  = 'https://herotime.co/signup/verify/' + str(challenge_hash) + "?email="+str(toEmail)
	msg_text = "Thank you for creating a HeroTime account. Click <a href=\"" + str(url) + "\">here</a> to verify your email."
	msg_html = "Thank you for creating a HeroTime account. Go to " + str(url) + " to verify your email."

	msg = create_msg('Password Verification', toEmail, toEmail, 'noreply@herotime.co', u'HeroTime')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg) 



@mngr.task
def send_recovery_email(toEmail, challenge_hash):
	url = 'https://herotime.co/newpassword/' + str(challenge_hash) + "?email=" + str(toEmail)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = "Click <a href=\"" + url + "\">here</a> to recover your HeroTime password."

	msg = create_msg('HeroTime password recovery requested.', toEmail, toEmail, 'noreply@herotime.co', u'HeroTime')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)



@mngr.task
def send_welcome_email(toEmail):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """\n<html><head></head><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = create_msg('Welcome to HeroTime', toEmail, toEmail, 'noreply@herotime.co', u'HeroTime')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(email_addr, msg)



@mngr.task
def send_email_change_email(toEmail, newEmail):
	msg_html = "Your HeroTime email has been changed to " + newEmail + ". If you did not make this change please let us know."

	msg = create_msg('HeroTime email address updated.', toEmail, toEmail, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(toEmail, msg)
	


@mngr.task
def send_passwd_change_email(toEmail):
	msg_html = "Your HeroTime password has been updated."

	msg = MIMEMultipart('alternative')
	msg = create_msg('HeroTime password updated.', toEmail, toEmail, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)



def send_proposal_reject_emails(the_proposal):
	print 'send proposal rejection notice to users'
	(hero_addr, hero_name, user_addr, user_name) = get_proposal_email_info(the_proposal)

	#TODO: Professionalize
	hero_msg_html = "Hey, hero you can put away your cape and cowl for now..  You rejected proposal %s from %s." % (the_proposal, user_name)
	hero_msg = create_msg('HeroTime proposal rejected', hero_addr, hero_name, 'noreply@herotime.co', u'HeroTime Notifications')
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_addr, hero_msg)

	buyer_msg_html = "Hey, keep your money.  Your hero is in another castle.  Your hero rejected your proposal %s." % (the_proposal)
	buyer_msg = create_msg('HeroTime proposal rejected', user_addr, user_name, 'noreply@herotime.co', u'HeroTime Notifications')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(user_addr, buyer_msg)



@mngr.task
def send_appt_emails(hero_email_addr, buyer_email_addr, appt):
	print 'sending appt emails@ ' + appt.ts_begin.strftime('%A, %b %d, %Y -- %H:%M %p')
	#TODO #CAH grab the profile names (see above, get_proposal_email_info)
	hero_msg_html = "Hey, Hero.  You have your cape and cowl.  You have an appointment on %s. was accepted." % (appt)
	hero_msg = create_msg('HeroTime appointment confirmation', hero_email_addr, hero_email_addr, 'noreply@herotime.co', u'HeroTime Notifications')
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_email_addr, hero_msg)

	buyer_msg_html = "Congrats.  You have an appointment setup on %s. was accepted." % (appt)
	buyer_msg = create_msg('HeroTime appointment confirmation', buyer_email_addr, buyer_email_addr, 'noreply@herotime.co', u'HeroTime Notifications')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)




def create_msg(subject, email_to, name_to, email_from, name_from):
	if (name_to == None):	name_to = email_to
	if (name_from == None):	name_from = email_from

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(name_to,	 'utf-8'), email_to)
	msg['From'] = "\"%s\" <%s>" % (Header(name_from, 'utf-8'), email_from)
	return msg


@mngr.task
def ht_send_email(toEmail, msg):
	# SendGrid login; TODO, move into config file.
	username = 'radnovic'
	password = "HeroTime"

	# Open a connection to the SendGrid mail server
	# sendmail function takes 3 arguments: sender's address, recipient's address
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@herotime.co', toEmail, msg.as_string())
	s.quit()
