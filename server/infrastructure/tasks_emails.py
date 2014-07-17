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
import json, smtplib, urllib




@mngr.task
def send_welcome_email(user_email, user_name):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """<html><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = create_msg('Welcome to HeroTime', user_email, user_name, 'noreply@herotime.co', u'HeroTime')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)




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
	msg_html = msg_html + "The request was for " + str(prop.get_prop_ts().strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.get_prop_tf().strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
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
	msg_html = msg_html + str(prop.get_prop_ts().strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.get_prop_tf().strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal to meet " + buyer_name  
	if (prop.prop_count > 1): msg_subject = msg_subject + " (updated)"

	msg = create_msg(msg_subject, hero_email, hero_name, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(hero_email, msg)




@mngr.task 
def send_verification_email(user_email, user_name, challenge_hash):
	""" Emails the account verification to the user. """
	url  = 'https://herotime.co/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email)
	msg_html = "Thank you for creating a HeroTime account. <a href=\"" + str(url) + "\">Verify your email address.</a><br>"  + str(challenge_hash)
	msg_text = "Thank you for creating a HeroTime account. Go to " + str(url) + " to verify your email."

	msg = create_msg('Verify your Insprite account', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)




@mngr.task
def ht_email_password_recovery_link(user_email, challenge_hash):
	""" Emails the password recovery link to a user """
	url = 'https://herotime.co/password/reset/' + str(challenge_hash) + "?email=" + str(user_email)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = email_body_recover_your_password(url)

	msg = create_msg('Reset your Insprite password', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)




@mngr.task
def ht_email_confirmation_of_changed_password(user_email):
	""" email user 'password changed' confirmation notice. """
	msg_html = email_body_updated_password_confirmation('url')
	msg_text = None	# TODO

	msg = create_msg('Your Insprite password has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	#msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)




@mngr.task
def ht_email_confirmation_of_changed_email_address(user_email, new_email):
	""" email user 'email address changed' confirmation noticed. """
	msg_html = email_body_updated_email_confirmation('url', new_email)
	msg_text = None

	msg = create_msg('Your Insprite email address has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(user_email, msg)




def ht_email_notice_of_proposal_rejection(the_proposal):
	""" email buyer (and seller?) the current proposal was rejected. """
	(hero_addr, hero_name, user_addr, user_name) = get_proposal_email_info(the_proposal)

	# we need to create a different notification if a user rejects another user's proposal.
	#hero_msg_html = email_body_proposal_rejected_to_seller(url, the_proposal)
	#hero_msg = create_msg("You rejected " + user_name + "'s proposal", hero_addr, hero_name, 'noreply@insprite.co', u'Insprite')
	#hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	#ht_send_email(hero_addr, hero_msg)


	# Emails sends the proposal rejection email to the buyer.
	buyer_msg_html = email_body_proposal_rejected_to_buyer(url, the_proposal)
	buyer_msg = create_msg(str(hero_name) + ' rejected your proposal', user_addr, user_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(user_addr, buyer_msg)




@mngr.task
def ht_email_meeting_reminder(user_email, user_name, prop_uuid):
	print 'ht_email_meeting_reminder()  sending appointment reminder emails now for ' + prop_uuid

	msg_html = "<p>Hey, " + user_name + ".</p><p>Your appointment " + prop_uuid + " is about to begin.</p>"
	msg = create_msg(' You Have an Appointment Tomorrow with {insert name}', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)




@mngr.task
def ht_email_review_notice(user_email, user_name, prop_uuid, review_id):
	print 'ht_email_review_notice()  sending meeting review emails now for ' + prop_uuid
	proposal = Proposal.get_by_id(prop_uuid)
	if (proposal.canceled()):
		print 'ht_email_review_notice()  meeting was canceled.  Do not send reviews. ' + prop_uuid
		return

	(sellr_acct, sellr_prof) = get_account_and_profile(proposal.prop_hero)
	(buyer_acct, buyer_prof) = get_account_and_profile(proposal.prop_user)
	partner_prof = sellr_prof
	if (sellr_acct.email == user_email):
		partner_prof = buyer_prof

	msg_html = "<p>Hey, " + user_name + ",</p>"
	msg_html = msg_html + "<p>Your meeting is over.<br>" + "When you have a few minutes, <a href=\"http://127.0.0.1:5000/review/"+prop_uuid+"/"+review_id+"\"> review your meeting.</a> "
	msg_html = msg_html + " with " + partner_prof.prof_name + " going over " + proposal.prop_desc + "</p>"
	msg = create_msg('Review Meeting with ' + partner_prof.prof_name, user_email, user_name, 'noreply@herotime.co', u'Insprite Notifications')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)




@mngr.task
def ht_email_meeting_accepted(the_proposal):
	""" email proposal accepted emails."""
	(sellr_addr, sellr_name, buyer_addr, buyer_name) = get_proposal_email_info(the_proposal)
	print 'sending proposal-accepted emails @ ' + the_proposal.get_prop_ts().strftime('%A, %b %d, %Y -- %H:%M %p')

	sellr_html = email_body_appointment_confirmation_for_seller(url, buyer_name, sellr_name)
	sellr_msg = create_msg('You accepted "' + user_name + 's proposal', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
	sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
	ht_send_email(sellr_addr, sellr_msg)

	# email buyer that seller accepted their proposal.
	buyer_html = email_body_appointment_confirmation_for_buyer(url, buyer_name, sellr_name)
	buyer_msg = create_msg(str(sellr_name) + ' accepted your proposal!', buyer_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
	ht_send_email(buyer_addr, buyer_msg)




def create_msg(subject, email_to, name_to, email_from, name_from):
	if (name_to == None):	name_to = email_to
	if (name_from == None):	name_from = email_from

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(name_to,	 'utf-8'), email_to)
	msg['From'] = "\"%s\" <%s>" % (Header(name_from, 'utf-8'), email_from)
	return msg




@mngr.task
def ht_send_email(email_addr, msg):
	# SendGrid login; TODO, move into config file.
	username = 'radnovic'
	password = "HeroTime"

	# open conn to SendGrid. Login send email.
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@herotime.co', email_addr, msg.as_string())
	s.quit()




def email_body_recover_your_password(url):
	""" HTML for sending the password recovery email """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="110" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:16px;">We get it&mdash;strong passwords can be tough to remember.<br><br>'
	msg = msg + 'No biggie, simply follow the instructions to change it at <a href="' + url  + '" style="color:#1488CC">' + url + '</a> and you\'ll be good to go.<br><br>'
	msg = msg + '\t\t\tDidn\'t request for a password reset?  <a href="mailto@thegang@insprite.co" style="color:#1488CC">Give us a holler ASAP</a>.</font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/facebookIcon.png">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/twitterIcon.png">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'


	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
	msg = msg + '\t\t| Sent by Insprite.co, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'
	return msg






def email_body_updated_email_confirmation(url, new_email):
  """HTML for email address change.	"""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">We\'re just sending you a reminder: You changed your email.<br><br>'
  msg = msg + '\t\t\t We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto@thegang@insprite.co" style="color:#1488CC">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'


  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#1488CC">Insprite.co</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg




def email_body_updated_password_confirmation(url):
  """ HTML email body for updated password. """
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">We\'re just sending you a reminder: You changed your password.<br><br>'
  msg = msg + '\t\t\t We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto@thegang@insprite.co" style="color:#1488CC">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'


  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#1488CC">Insprite.co</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
 


def email_body_proposal_rejected_to_buyer(url, proposal):
  """ generate email body (HTML).  the proposal was rejected email, will be sent to the buyer."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> {insert hero_name} didn\'t accept your proposal this time around.<br><br>'
  msg = msg + '\t\t\t Why, you ask? There could be many reasons, but trust us, don\'t take it personally. <br><br>'
  msg = msg + '\t\t\t Need to edit, manage or update the appointment? Go for it, or follow up with {insert hero_name} </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'


  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#1488CC">Insprite.co</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg



def email_body_appointment_confirmation_for_buyer(url, buyer_name, sellr_name, sellr_profile_id="SELLER_PROFILE_ID", msg_url="https://127.0.0.1:5000/message?profile=xxxx"):
  """HTML email for buyer after seller accepts the proposal."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Ain\'t life grand? Meeting\'s on! <a href="https://127.0.0.1:5000/profile?'+ sellr_profile_id + ' style="color:#1488CC">"' + sellr_name + '" accepted your proposal.</a><br><br>'
  msg = msg + '\t\t\t Check out the details: {Corey insert details} <br>'
  msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="'+msg_url+'" style="color:#1488CC">"' + sellr_name + '" a message.</a><br><br></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'


  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#1488CC">Insprite.co</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg




def email_body_appointment_confirmation_for_seller(url, buyer_name, sellr_name, buyer_profile='prof_id', msg_user_link='https://INSPRITE.co/message/USER'):
  """HTML email for seller.  Confirmation that s/he accepted the proposal."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Fantastic! You accepted <a href="https://127.0.0.1:5000/profile?' + buyer_profile + '" style="color:#1488CC">' + buyer_name + '\'s proposal.</a><br><br>'
  msg = msg + '\t\t\t Check out the details:<br> {Corey insert details} <br>'
  msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="' + msg_user_link + '" style="color:#1488CC"> ' + buyer_name + ' a message.</a><br><br>We know life can be busy, so we\'ll send you a reminder 24 hours in advance too.</font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'


  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#1488CC">Insprite.co</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg

def email_body_cancellation_from_buyer():
  """ generate email body (HTML).  The buyer cancels the appointment later than 24 hours."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Shucks. You cancelled your appointment. Thanks for letting <a href="#" style="color:#29abe1">{insert seller name}</a> know ahead of time; you will not be charged for the cancellation.<br><br>'
  msg = msg + '\t\t\t Need to reschedule? Go right ahead. <br><br>'
  msg = msg + '\t\t\t You can also explore other options, too. </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg

def email_body_24_hour_cancellation_from_buyer():
  """ generate email body (HTML).  The buyer cancels the appointment within the 24 hours and will be charged."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> You cancelled the appointment with <a href="#" style="color:#29abe1">{insert seller name}</a>.<br><br>'
  msg = msg + '\t\t\t We know life can be busy, but we also value accountability within the community and adhere to a <a href="#" style="color:#29abe1">24-hour cancellation policy</a>. You will be charged <a href="#" style="color:#29abe1">{$ insert fee}</a> for the service. <br><br>'
  msg = msg + '\t\t\t Questions? <a href="#" style="color:#29abe1">Drop us a line</a> or read our <a href="#" style="color:#29abe1">Terms of Service</a> and <a href="#" style="color:#29abe1">cancellation policies</a> for additional information. </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg

def email_body_appt_reminder():
  """ generate email body (HTML). Both parties should receive 24 hours in advance of the meeting."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'
  
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Drats. <a href="#" style="color:#29abe1">{insert seller name} cancelled your appointment</a>.<br><br>'
  msg = msg + '\t\t\t <a href="#" style="color:#29abe1">Reschedule</a> or you can send a message to inquire about the cancellation. <br><br>'
  msg = msg + '\t\t\t And, don\'t worry! You won\'t be charged, promise. </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_msg_to():
  """ generate email body (HTML).  Notification when a user sends a message."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Way to get the conversation started! You messaged <a href="#" style="color:#29abe1">{insert user name}</a> and should get a response soon.<br><br>'
  msg = msg + '\t\t\t Until then, stand tight. <br><br>'
  msg = msg + '</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_msg_received():
  """ generate email body (HTML).  Notification when seller receives a new proposal."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
  msg = msg + '\t\t<<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">You\'ve got mail. It\'s from <a href="#" style="color:#29abe1">{user\'s name}</a>.<br>'
  msg = msg + '\t\t\t <i>{insert messaged}</i></font><br>'
  msg = msg + '</td></tr>'
  
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:200px" align="left" valign="top">'
  msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #29abe1;font-size: 14px;border-radius: 3px;border: 1px solid #29abe1;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center;" target="_blank">Reply</a>'
  msg = msg + '</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_verify_account():
  """ HTML for verifying a user account """
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#fffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'
 
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
  msg = msg + '\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px; padding-left:85px; padding-right:85px; padding-bottom:25px" align="left" valign="top">'
  msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Welcome to Insprite! We\'re thrilled that you\'ve joined us.<br><br>'
  msg = msg + 'Insprite lets you connect with and learn from the creative people around you, and to teach your passions and skills to others. We think you\'ll love exploring our growing community!<br><br>'
  msg = msg + 'Before you explore the cool things you can learn and experience from the inspiring, creative people around you (or decide to be one of them), please verify your email account so we know you\'re a real breathing human.<br><br>'
  msg = msg + 'If you\'re getting this message by mistake and didn\'t create an account, <a href="mailto@thegang@insprite.co" style="color:#29abe1">drop us a line</a> and we\'ll get on it ASAP.</font>'
  msg = msg + '</td></tr>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600" height="200">'
  msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="center" valign="top">'
  msg = msg + '<a href="#" style="color:#ffffff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:999em;margin-top:15px;margin-left:5px;font-family:Garamond, EB Garamond, Georgia, serif;" target="_blank">Verify your account</a>'
  msg = msg + '</td></tr></table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png"><img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '<img src="http://ryanfbaker.com/insprite/instagramIcon.png"></td></tr></table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '<img src="http://ryanfbaker.com/insprite/spacer-2.png"></td></tr></table>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a> | Sent by <a href="http://www/insprite.co" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '</td></tr></table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;" align="left" valign="middle">'
  msg = msg + '<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png"></td></tr></table>'
  return msg
  
def email_body_new_proposal():
  """ generate email body (HTML).  Notification when seller receives a new proposal."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
  msg = msg + '\t\t<<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Great! You received a new proposal from <a href="#" style="color:#29abe1">{user\'s name}</a>. <br><br>'
  msg = msg + '\t\t\t <br>Day: <br>Time <br>Duration: <br>Location:<br>Fee:<br><br></font> <br><br>'
  msg = msg + '</td></tr>'
  
  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:200px" align="left" valign="top">'
  msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #29abe1;font-size: 14px;border-radius: 3px;border: 1px solid #29abe1;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center;" target="_blank">Accept</a>'
  msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #e55e62;font-size: 14px;border-radius: 3px;border: 1px solid #e55e62;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center" target="_blank">Reject</a>'
  msg = msg + '</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  

def email_body_rejected_from_seller():
  """ generate email body (HTML).  Seller rejects proposal and receives this email."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">You did not accept a proposal from <a href="#" style="color:#29abe1">{insert buyer name}</a>.<br><br>'
  msg = msg + '\t\t\t Message <a href="#" style="color:#29abe1">{insert buyer name}</a> to see if you can work our a new date and time. </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_review():
  """ generate email body (HTML).  Rate and review email, both buyer and seller."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr>td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px; padding-right:75px" align="left" valign="top">'
  msg = msg + '\t\t <font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">We hope you had a great appointment!<br>'
  msg = msg + '\t\t\t Your opinion goes a long way&mdash;write up your review of the appointment so others can learn from your experience with <a href="#" style="color:#29abe1">{user\'s name}</a></font><br><br>'
  msg = msg + '\t</td></tr>'

  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:200px" align="left" valign="top">'
  msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #29abe1;font-size: 14px;border-radius: 3px;border: 1px solid #29abe1;font-family:Garamond, EB Garamond, Georgia, serif; width:100px;text-align:center;" target="_blank">Rate & Review</a>'
  msg = msg + '</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_beta_email(url):
  """ HTML for sending the beta email """
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
  msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Thanks for signing up for Insprite! We are excited that you\'re interested in what we are doing over here. We are creating Insprite to be a vibrant, friendly community where you can both learn from creative people in your area, and teach your passions to others. We sincerely hope that you will be a part of it!'
  msg = msg + '<br><br>We\'re currently in the process of finishing up Insprite... and we\'re nearly there. We\'re just adding some bells and whistles on it so it\'ll be the best possible experience for you.<br><br>'
  msg = msg + 'We will be in touch when we\'re getting ready to launch&mdash;tentatively in late 2014. We can\'t wait to show you what we\'ve been working on. You\'re going to love it.<br><br>'
  msg = msg + 'In the meantime, feel free to drop us a line, or follow us on our <a href="#" style="color:#29abe1">Blog</a>, where we will post lots of cool bloggy things (no, really, we\'re gonna try and keep it interesting).<br><br>'
  msg = msg + '<br>Spritely yours,<br>'
  msg = msg + 'The Insprite Gang </font>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

def email_body_48_hour_cancellation_email_to_seller():
  """ generate email body (HTML).  Buyer cancels the meeting within 48 hours and seller receives this email."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Drats. <a href="#" style="color:#29abe1">{Insert user - buyer}</a> cancelled your appointment.<br><br>'
  msg = msg + '\t\t\t Message <a href="#" style="color:#29abe1">{insert buyer name}</a> to see if you can work out a new date and time. </font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg

def email_body_24_hour_cancellation_email_to_seller():
  """ generate email body (HTML).  Buyer cancels the meeting within 24 hours and seller receives this email."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> <a href="#" style="color:#29abe1">{Insert user - buyer}</a> cancelled your appointment.<br><br>'
  msg = msg + '\t\t\t Sometimes things come up in life, but your time and talent are still valuable. You\'ll receive {insert fee} from {insert buyer} for the cancelled booking.</font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
  
def email_body_cancellation_email_to_buyer():
  """ generate email body (HTML).  Seller cancels the meeting, sends this email to buyer."""
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> <a href="#" style="color:#29abe1">{Insert user - seller}</a> cancelled your appointment.<br><br>'
  msg = msg + '\t\t\t Check out <a href="#" style="color:#29abe1">{Insert seller}</a>\'s availability, and send a new proposal. (Sometimes, a little reshuffling can really make things happen!)</font><br><br>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
  msg = msg + '\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg