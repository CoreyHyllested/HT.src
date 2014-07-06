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


#Email account verification for the buyer. 
@mngr.task 
def send_verification_email(user_email, user_name, challenge_hash):
	url  = 'https://herotime.co/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email)
	msg_html = "Thank you for creating a HeroTime account. <a href=\"" + str(url) + "\">Verify your email address.</a><br>"  + str(challenge_hash)
	msg_text = "Thank you for creating a HeroTime account. Go to " + str(url) + " to verify your email."

	msg = create_msg('Verify your Insprite account', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)

#Email password recovery link. 
@mngr.task
def send_recovery_email(toEmail, challenge_hash):
	url = 'https://herotime.co/password/reset/' + str(challenge_hash) + "?email=" + str(toEmail)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = gen_recovery_msg(url)
	#"Click <a href=\"" + url + "\">here</a> to recover your HeroTime password."

	msg = create_msg('Reset your Insprite password', toEmail, toEmail, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)

#HTML password recovery email.
def gen_recovery_msg(url):
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
	msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
	msg = msg + '\t</td></tr>'

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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:16px;">We get it&mdash;passwords can be tough to remember.<br><br>'
	msg = msg + '\t\t\t No biggie, simply follow the instructions to change it at <a href="' + url  + '" style="color:#29abe1">' + url + '</a> and you\'ll be good to go.<br><br>'
	msg = msg + '\t\t\tDidn\'t request for a password reset?  <a href="mailto@thegang@insprite.co" style="color:#29abe1">Give us a holler ASAP</a>.</font>'
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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
	msg = msg + '\t\t| Sent by Insprite.co, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'
	return msg


@mngr.task
def send_welcome_email(user_email, user_name):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """<html><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = create_msg('Welcome to HeroTime', user_email, user_name, 'noreply@herotime.co', u'HeroTime')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)


#Email sent if user changes email address.
@mngr.task
def send_email_change_email(toEmail, newEmail):
	msg_html = gen_email_change_msg(url)

	msg = create_msg('You Insprite email has been updated', toEmail, toEmail, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(toEmail, msg)
	
#HTML for email address change.	
def gen_email_change_msg(url):
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
  msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
  msg = msg + '\t</td></tr>'

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
  msg = msg + '\t\t\t We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto@thegang@insprite.co" style="color:#29abe1">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
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
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg


#Email if user changes password.
@mngr.task
def send_passwd_change_email(toEmail):
	msg_html = gen_password_change_msg(url)

	msg = MIMEMultipart('alternative')
	msg = create_msg('Your Insprite password has been updated', toEmail, toEmail, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)

#HTML for email address change.
def gen_password_change_msg(url):
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
  msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
  msg = msg + '\t</td></tr>'

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
  msg = msg + '\t\t\t We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto@thegang@insprite.co" style="color:#29abe1">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
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
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
 

#Emails sends the proposal rejection emails to the buyer. 
def send_proposal_reject_emails(the_proposal):
	print 'send proposal rejection notice to user'
	(hero_addr, hero_name, user_addr, user_name) = get_proposal_email_info(the_proposal)

# #TODO: Professionalize
# #Emails sends the proposal rejection to the seller.
# 	hero_msg_html = send_proposal_reject_emails_seller(url) # "Hey, hero you can put away your cape and cowl for now..  You rejected proposal %s from %s." % (the_proposal, user_name)
# 	hero_msg = create_msg("You rejected " + user_name + "'s proposal", hero_addr, hero_name, 'noreply@insprite.co', u'Insprite')
# 	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
# 	ht_send_email(hero_addr, hero_msg)


#Emails sends the proposal rejection email to the buyer.
	buyer_msg_html = send_proposal_reject_emails_buyer(url) # "Hey, keep your money.  Your hero is in another castle.  Your hero rejected your proposal %s." % (the_proposal)
	buyer_msg = create_msg(str(hero_name) + ' rejected your proposal', user_addr, user_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(user_addr, buyer_msg)

#HTML proposal rejection email to the buyer.
def send_proposal_reject_emails_buyer(url):
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
  msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
  msg = msg + '\t</td></tr>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
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
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
 

#Email sends the message...?
@mngr.task
def ht_send_reminder_email(user_email, user_name, the_proposal):
	print 'sending appointment reminder emails now for ', the_proposal

	msg_html = "<p>Hey, " + user_name + ".</p><p>Your appointment" + str(the_proposal) + "is about to begin.</p>"
	msg = create_msg('HeroTime Appointment Reminder', user_email, user_name, 'noreply@herotime.co', u'HeroTime Notifications')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)



#Email for appointments after accepting proposal.
@mngr.task
def send_appt_emails(the_proposal):

	(sellr_addr, sellr_name, buyer_addr, buyer_name) = get_proposal_email_info(the_proposal)
	print 'sending proposal-accepted emails @ ' + the_proposal.prop_ts.strftime('%A, %b %d, %Y -- %H:%M %p')

	sellr_html = sellr_receives_accepted_proposal(url)
	sellr_msg = create_msg('You accepted "' + user_name + 's proposal', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
	sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
	ht_send_email(sellr_addr, sellr_msg)

	#HTML for seller after accepting the proposal.
def sellr_receives_accepted_proposal(url):
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
  msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
  msg = msg + '\t</td></tr>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Fantastic! You accepted <a href="#" style="color:#29abe1"> {buyer name} proposal.</a><br><br>'
  msg = msg + '\t\t\t Check out the details:<br> {Corey insert details} <br>'
  msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="#" style="color:#29abe1">Go for it</a>, or send <a href="#" style="color:#29abe1"> {insert buyer name} a message.</a><br><br>We know life can be busy, so we\'ll send you a reminder 24 hours in advance, too.</font>'
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
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg
	
#Old code.	
# 	"<p>IMG_LOGO</p><br>"																					\
# 				+"<p>Fantastic!<br>You accepted " + sellr_name + "'s proposal.</p>"										\
# 				+"<p>Here are the details:<br>"																			\
# 				+"Location: " + the_proposal.prop_place + "<br>"														\
# 				+"Description: " + the_proposal.prop_desc + "<br>"														\
# 				+"Time: " + str(the_proposal.prop_ts.strftime('%A, %b %d, %Y -- %H:%M %p')) 							\
# 				+"</p>"																									\
# 				+"<p>We know life can be busy, so we'll send you a reminder 48 hours before the meeting starts.<br>"	\
# 				+"Questions? Drop us a line at <a href=\"mailto:thegang@insprite.co\">thegang@insprite.co<a>"			\
# 				+"</p>"																									\
# 				+"<p>FOOTER.  Sent by Insprite. - California, USA</p>"


	#Email for buyer after seller accepts the proposal.
  buyer_html = buyer_receives_accepted_proposal(url)
  buyer_msg = create_msg(str(sellr_name) + ' accepted your proposal!', buyer_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
  buyer_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
  ht_send_email(buyer_addr, buyer_msg)

#HTML email for buyer after seller accepts the proposal.	
def buyer_receives_accepted_proposal(url):
  msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
  msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
  msg = msg + '<tbody>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #000000; text-align: center; height: 25px;" align="center">'
  msg = msg + '\t\t<span style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none;">Having trouble viewing this email? <a style="font-size: 10px; color: #575757; line-height: 200%; font-family: Helvetica Neue; text-decoration: none; font-weight: bold;" href="#">View it in your browser.</a></span>'
  msg = msg + '\t</td></tr>'

  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
  msg = msg + '\t\t<a href="http://www.insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</tbody>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
  msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
  msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Ain\'t life grand? Meeting\'s on! <a href="#" style="color:#29abe1">"' + sellr_name + '" accepted your proposal.</a><br><br>'
  msg = msg + '\t\t\t Check out the details: {Corey insert details} <br>'
  msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="#" style="color:#29abe1">Go for it</a>, or send <a href="#" style="color:#29abe1">"' + sellr_name + '" a message.</a><br><br></font>'
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
  msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto@thegang@insprite.co" style="color:#29abe1">Contact Us</a>'
  msg = msg + '\t\t| Sent by <a href="#" style="color:#29abe1">Insprite.co</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'

  msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
  msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
  msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
  msg = msg + '\t</td></tr>'
  msg = msg + '</table>'
  return msg

#Old code.			
#				  +"<p>Ain't Life Grand?<br>Meeting's on! " + sellr_name + " accepted your proposal.</p>"	\
# 				+"<p>Check out the details:<br>"	\
# 				+"Location: " + the_proposal.prop_place + "<br>"	\
# 				+"Description: " + the_proposal.prop_desc + "<br>"	\
# 				+"Time: " + str(the_proposal.prop_ts.strftime('%A, %b %d, %Y -- %H:%M %p')) + "<br>"	\
# 				+"</p>"	\
# 				+"<p>Need to edit, manage, or *gasp* cancel your appointment?  Head to your <a href=\'https://127.0.0.1:5000/dashboard\'>dashboard</a>"	\
# 				+"We know life can be busy, so we'll send you a reminder 48 hours before the meeting starts.<br>"	\
# 				+"Questions? Drop us a line at <a href=\"mailto:thegang@insprite.co\">thegang@insprite.co<a>"	\
# 				+"</p>"	\
# 				+"<p>FOOTER.  Sent by Insprite. - California, USA</p>"	\
# 				+"<p>UNSUBSCRIBE.  SOCIAL PLUGINS.</p>"



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
