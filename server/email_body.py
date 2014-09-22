#################################################################################
# Copyright (C) 2014 Insprite, LLC.
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
from server.infrastructure.srvc_database import db_session
from server.models		 import *
from server.infrastructure.errors		 import *
import json, urllib


header = '<!DOCTYPE html>\n<html>\n<body style=margin:0px>\n<table cellspacing=0 cellpadding=20 width=100% bgcolor=#f0f0f0>\n<tbody>\n<tr>\n<td>\n<table cellspacing=0 cellpadding=0 width=60% align=center bgcolor=#fff>\n<tbody>\n<tr>\n<td>\n<table cellspacing=0 cellpadding=10 width=100%>\n<tbody>\n<tr>\n<td style=padding-bottom:10px;padding-top:35px align=center valign=middle>\n<a href=http://www.insprite.co><img src=http://insprite.co/static/img/email/insprite_maroon.png border=0 alt=Insprite align=center width=300px height=41px /></a>\n</td>\n</tr>\n</tbody>\n</table>\n'

footer = '<table cellspacing=0 cellpadding=0 width=100% style=padding-top:80px>\n<tr>\n<td style=padding-bottom:5px align=center valign=middle>\n<a href=http://www.facebook.com/insprite><img style=padding-right:12px src=http://insprite.co/static/img/email/facebookIcon.png></a>\n<a href=http://www.twitter.com/inspriting><img style=padding-right:12px src=http://insprite.co/static/img/email/twitterIcon.png></a>\n<a href=http://www.instagram.com/inspriting><img style=padding-right:12px src=http://insprite.co/static/img/email/instagramIcon.png></a>\n<a href=http://www.pinterest.com/insprite><img src=http://insprite.co/static/img/email/pinterestIcon.png></a>\n</td>\n</tr>\n</table>\n<table cellspacing=0 cellpadding=0 width=100%>\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:5px solid #fff" align=center valign=middle>\n<img src=http://insprite.co/static/img/email/spacer-2.png>\n</td>\n</tr>\n</table>\n<table cellspacing=0 cellpadding=0 width=100%>\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:10px solid #fff" align=center valign=middle>\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:10px"> <a href=mailto:thegang@insprite.co style=color:#1488CC>Contact Us</a> | Sent by <a href=http://www.insprite.co style=color:#1488CC>Insprite.co</a>, Berkeley, California, USA.</font>\n</td>\n</tr>\n</table>\n<table cellspacing=0 cellpadding=0 width=100% background=http://insprite.co/static/img/email/footerImage.png bgcolor=#e75f63>\n<tr>\n<td align=center valign=middle style=height:80px>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</tbody>\n</table>\n</td>\n</tr>\n</tbody>\n</table>\n</body>\n</html>'


def email_body_verify_account(verify_email_url):
	""" HTML for verifying user account; called by ht_email_welcome_message() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nPlease verify your email account before you start exploring the cool, creative experiences you can have near you.<br><br>\nIf you are getting this message by mistake and did not create an account, <a href="mailto@thegang@insprite.co" style="color:#e75f63">let us know</a> and we will get on it ASAP.\n</font>\n</td>\n</tr>\n</table>\n<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:10px solid #fff;padding-top:0" align="center" valign="top">\n<a href="'+verify_email_url+'" style="color:#fff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:999em;margin-top:15px;margin-left:5px;font-family:Helvetica Neue,Arial,sans-serif" target="_blank">Verify your account</a>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_recover_your_password(url):
	""" HTML for sending the password recovery email; ht_send_password_recovery_link() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nPasswords can be tough to remember. No biggie, simply <a href=\"' + url + '\" style="color:#1488CC">follow the instructions to change it</a> and you will be good to go.<br><br>\nDid not request for a password reset? <a href="mailto@thegang@insprite.co" style="color:#e75f63">Let us know ASAP</a>.</font>\n</font>\n</td>\n</tr>\n</table>' +footer

	return msg


def email_body_password_changed_confirmation(url):
	""" HTML email body for updated password. sent via ht_send_password_changed_confirmation() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWe are sending you a reminder: You changed your password.<br><br>\nWe want to keep your information safe and secure, so if you did not change it yourself <a href="mailto@thegang@insprite.co" style="color:#e75f63">let us know ASAP</a> and we will get on it.\n</font>\n</td>\n</tr>\n</table>' + footer
	return msg
 

# def email_body_verify_email_address(url, code):  #bug267
# 	"""HTML for email address verification; sent via  ht_send_email_address_verify_link() """
# 	msg = ""
# 	return msg



def email_body_email_address_changed_confirmation(url, new_email):
	"""HTML for email address change; sent via  ht_send_email_address_changed_confirmation() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWe are sending you a reminder: You changed your email.<br><br>\nWe want to keep your information safe and secure, so if you did not change it yourself <a href="mailto@thegang@insprite.co" style="color:#e75f63">let us know ASAP</a> and we will get on it.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


################################################################################
### PROPOSAL | APPOINTMENT | MEETING EMAILS ####################################
################################################################################


def email_body_new_proposal_notification_to_seller(meeting, buyer_name, buyer_profile_id):
	""" generate email body (HTML).  Notification when seller receives a new meeting proposal.  Sent via ht_send_sellr_proposal_update(). """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">\n<tbody>\n\t<tr><td align="center" valign="top">\n\t</td></tr>\n</tbody>\n</table>'

	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">'
	msg = msg + '\n<tbody><tr>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '\n\t\t<tbody>'
	msg = msg + '\n\t\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\n\t\t\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" />'
	msg = msg + '\n\t\t\t\t</a>'
	msg = msg + '\n\t\t\t</td></tr>'
	msg = msg + '\n\t\t</tbody>'
	msg = msg + '\n\t</table>'


	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">'
	msg = msg + '\n\t\t\t\tGreat! You received a new proposal from <a href=\"https://127.0.0.1:5000/profile?hero=' + buyer_profile_id + '\" style="color:#1488CC">'+ buyer_name + '</a>.'
	msg = msg + '\n\t\t\t\t<br><br><br>'
	msg = msg + '\n\t\t\t\tTime: ' + meeting.meet_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + meeting.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(meeting.meet_location) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(meeting.meet_cost) + '<br><br>'
	msg = msg + '\n\t\t\t\tDescription: ' + meeting.get_description_html() + '<br><br>'
	msg = msg + '\n\t\t\t</font><br><br>'
	msg = msg + '\n\t\t</td></tr>'

	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:150px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<a href=\"'+ meeting.accept_url() +'\" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #1488CC;font-size: 14px;border-radius: 3px;border: 1px solid #1488CC;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center;" target="_blank">Accept</a> '
	msg = msg + '\n\t\t\t<a href=\"'+ meeting.reject_url() +'\" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #e55e62;font-size: 14px;border-radius: 3px;border: 1px solid #e55e62;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center" target="_blank">Reject</a> '
	msg = msg + '\n\t\t</td></tr>'
	msg = msg + '\n\t</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
	msg = msg + '\n\t\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
	msg = msg + '\n\t\t</td></tr>'
	msg = msg + '\n\t</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\n\t\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
	msg = msg + '\n\t\t</td></tr>'
	msg = msg + '\n\t</table>'

	msg = msg + '\n</tr></tbody>'
	msg = msg + '</table>'
	return msg




def email_body_meeting_rejected_notification_to_buyer(meeting, sellr_name):
	""" generate email body (HTML).  Buyer receives this email; sent via ht_send_meeting_rejected_notifications. """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">\n<tbody>\n\t<tr>\n\t\t<td align="center" valign="top"></td>\n\t</tr>\n</tbody>\n</table>\n\n'

	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">'
	msg = msg + '\n<tbody>'
	msg = msg + '\n\t<tr>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '\n\t\t\t<tbody>'

	msg = msg + '\n\t\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\n\t\t\t\t\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\n\t\t\t\t\t</td>'
	msg = msg + '\n\t\t\t\t</tr>'
	msg = msg + '\n\t\t\t</tbody>'
	msg = msg + '\n\t\t</table>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\n\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\n\t\t\t\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">'
	msg = msg + '\n\t\t\t\t\t\t' + sellr_name + ' didn\'t accept your proposal this time around.<br><br>'
	msg = msg + '\n\t\t\t\t\t\tWhy, you ask? There could be many reasons, but trust us, don\'t take it personally. <br><br>'
	msg = msg + '\n\t\t\t\t\t\tNeed to edit, manage or update the appointment? Go for it, or follow up with ' + sellr_name + '.'
	msg = msg + '\n\t\t\t\t\t</font><br><br>'
	msg = msg + '\n\t\t\t\t</td>'
	msg = msg + '\n\t\t\t</tr>'
	msg = msg + '\n\t\t</table>'

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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto:thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
	msg = msg + '\t\t| Sent by <a href="https://insprite.co" style="color:#1488CC">Insprite</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'
	return msg




def email_body_meeting_rejected_notification_to_seller(meeting, buyer_name, buyer_prof_id):
	""" generate email body (HTML).  Seller rejects proposal and receives this email; sent via ht_send_meeting_rejected_notifications. """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">\n<tbody>\n\t<tr>\n\t\t<td align="center" valign="top">\n\t\t</td>\n\t</tr>\n</tbody>\n</table>\n\n'

	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff">'
	msg = msg + '\n<tbody>'
	msg = msg + '\n\t<tr>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '\n\t\t\t<tbody>'
	msg = msg + '\n\t\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\n\t\t\t\t\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\n\t\t\t\t\t</td>'
	msg = msg + '\n\t\t\t\t</tr>'
	msg = msg + '\n\t\t\t</tbody>'
	msg = msg + '\n\t\t</table>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\n\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\n\t\t\t\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">'
	msg = msg + '\n\t\t\t\t\t\tYou did not accept a proposal from <a href=\"https://127.0.0.1:5000/profile?hero=\"' + buyer_prof_id + ' style="color:#1488CC">' + buyer_name + '</a>.<br><br>'
	msg = msg + '\n\t\t\t\t\t\tMessage <a href="#" style="color:#1488CC">' + buyer_name + '</a> to see if you can work our a new date and time.'
	msg = msg + '\n\t\t\t\t\t</font><br><br>'
	msg = msg + '\n\t\t\t\t</td>'
	msg = msg + '\n\t\t\t</tr>'
	msg = msg + '\n\t\t</table>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\n\t\t\t\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
	msg = msg + '\n\t\t\t\t\t<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
	msg = msg + '\n\t\t\t\t\t<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
	msg = msg + '\n\t\t\t\t</td>'
	msg = msg + '\n\t\t\t</tr>'
	msg = msg + '\n\t\t</table>'

	msg = msg + '\n\t\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t\t<tr>'
	msg = msg + '\n\t\t\t\t<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '\n\t\t\t\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
	msg = msg + '\n\t\t\t\t</td>'
	msg = msg + '\n\t\t\t</tr>'
	msg = msg + '\n\t\t</table>'

	msg = msg + '\n\t</tr>'
	msg = msg + '\n</tbody>'
	msg = msg + '</table>'
	return msg


 


def email_body_appointment_confirmation_for_buyer(meeting, buyer_profile, sellr_profile, msg_url="https://127.0.0.1:5000/message?profile=xxxx"):
	"""HTML email for buyer after the meeting proposal is accepted; called from ht_send_meeting_accepted_notification """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Ain\'t life grand? Meeting\'s on! <a href="https://127.0.0.1:5000/profile?'+ sellr_profile.prof_id + ' style="color:#1488CC">"' + sellr_profile.prof_name + '" accepted your proposal.</a><br><br>'
	msg = msg + '\t\t\t Check out the details: <br>'
	msg = msg + '\n\t\t\t\tTime: ' + meeting.meet_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + meeting.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(meeting.meet_location) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(meeting.meet_cost) + '<br><br>'
	msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="'+msg_url+'" style="color:#1488CC">"' + sellr_profile.prof_name + '" a message.</a><br><br></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://maps.googleapis.com/maps/api/staticmap?center=' + meeting.meet_location + '&zoom=15&size=400x450&markers=size:large%8Ccolor:0xFFFF00%7Clabel:Insprite%7C' + meeting.meet_location + '">'
	msg = msg + '\n\t\t</td></tr>'
	msg = msg + '\n\t</table>'


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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto:thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
	msg = msg + '\t\t| Sent by <a href="https://insprite.co" style="color:#1488CC">Insprite</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\t<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '\t\t<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'
	return msg




def email_body_appointment_confirmation_for_seller(meeting, buyer_profile, sellr_profile, msg_user_link='https://INSPRITE.co/message/USER'):
	"""HTML email for seller after accepted meeting proposal; called from ht_send_meeting_accepted_notification """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'

	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Fantastic! You accepted <a href="https://127.0.0.1:5000/profile?' + buyer_profile.prof_id + '" style="color:#1488CC">' + buyer_profile.prof_name + '\'s proposal.</a><br><br>'
	msg = msg + '\t\t\t Check out the details:<br>'
	msg = msg + '\n\t\t\t\tTime: ' + meeting.meet_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + meeting.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(meeting.meet_location) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(meeting.meet_cost) + '<br><br>'
	msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="' + msg_user_link + '" style="color:#1488CC"> ' + buyer_profile.prof_name + ' a message.</a><br><br>We know life can be busy, so we\'ll send you a reminder 24 hours in advance too.</font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://maps.googleapis.com/maps/api/staticmap?center=' + meeting.meet_location + '&zoom=15&size=400x450&markers=size:large%8Ccolor:0xFFFF00%7Clabel:Insprite%7C' + meeting.meet_location + '"><br>'
	msg = msg + '\n\t\t</td></tr>'
	msg = msg + '\n\t</table>'


	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/facebookIcon.png">'
	msg = msg + '<img style="padding-right: 6px" src="http://ryanfbaker.com/insprite/twitterIcon.png">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/instagramIcon.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"><a href="mailto:thegang@insprite.co" style="color:#1488CC">Contact Us</a> '
	msg = msg + '| Sent by <a href="https://insprite.co" style="color:#1488CC">Insprite</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font><br>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'
	return msg




def email_body_cancellation_from_buyer_outside_24_hours(buyer_name, sellr_name):
	""" generate email body (HTML).  The buyer cancels the appointment in advance of 24 hours threshold. sent via ht_send_meeting_canceled_notifications """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Shucks. You cancelled your appointment. Thanks for letting <a href="#" style="color:#1488CC">' + sellr_name + '</a> know ahead of time; you will not be charged for the cancellation.<br><br>'
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
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #e6e6e6;" align="center" valign="middle">'
	msg = msg + '\t\t<img src="http://ryanfbaker.com/insprite/spacer-2.png">'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'
	return msg




def email_body_cancellation_from_buyer_within_24_hours(sellr_name, cost):
	""" generate email body (HTML).  The buyer canceled the appointment within the 24 hours and will be charged.; sent via ht_send_meeting_canceled_notifications """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> You cancelled the appointment with <a href="#" style="color:#1488CC">' + sellr_name + '</a>.<br><br>'
	msg = msg + '\t\t\t We know life can be busy, but we also value accountability within the community and adhere to a <a href="#" style="color:#1488CC">24-hour cancellation policy</a>. You will be charged <a href="#" style="color:#1488CC">$' + str(cost) + '</a> for the service. <br><br>'
	msg = msg + '\t\t\t Questions? <a href="#" style="color:#1488CC">Drop us a line</a> or read our <a href="#" style="color:#1488CC">Terms of Service</a> and <a href="#" style="color:#1488CC">cancellation policies</a> for additional information. </font><br><br>'
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




def email_body_cancellation_from_buyer_within_24_hours_to_seller(buyer_name, cost):
	""" generate email body (HTML).  Buyer cancels the meeting within 24 hours and seller receives this email. sent via ht_send_meeting_canceled_notifications """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> <a href="#" style="color:#1488CC"> ' + buyer_name + ' </a> cancelled your appointment.<br><br>'
	msg = msg + '\t\t\t Sometimes things come up in life, but your time and talent are still valuable. You\'ll receive '+ str(cost) +' from ' + buyer_name + ' for the cancelled booking.</font><br><br>'
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




def email_body_cancellation_from_buyer_within_48_hours_to_seller(buyer_name):
	""" generate email body (HTML).  Buyer cancels the meeting within 48 hours and seller receives this email.; ht_send_meeting_canceled_notifications """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Drats. <a href="#" style="color:#1488CC">' + buyer_name + '</a> cancelled your appointment.<br><br>'
	msg = msg + '\t\t\t Message <a href="#" style="color:#1488CC">'+buyer_name+'</a> to see if you can work out a new date and time. </font><br><br>'
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




def email_body_cancellation_from_seller_to_buyer():
	""" generate email body (HTML).  Seller cancels the meeting, sends this email to buyer; sent via ht_send_meeting_canceled_notifications"""
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> <a href="#" style="color:#1488CC">{Insert user - seller}</a> cancelled your appointment.<br><br>'
	msg = msg + '\t\t\t Check out <a href="#" style="color:#1488CC">{Insert seller}</a>\'s availability, and send a new proposal. (Sometimes, a little reshuffling can really make things happen!)</font><br><br>'
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




################################################################################
### DELAYED REMINDERS (MEETING, REVIEWS) #######################################
################################################################################

def email_body_meeting_reminder():
	""" generate email body (HTML). Both parties should receive 24 hours in advance of the meeting; sent by ht_send_meeting_reminder() """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Drats. <a href="#" style="color:#1488CC">{insert seller name} cancelled your appointment</a>.<br><br>'
	msg = msg + '\t\t\t <a href="#" style="color:#1488CC">Reschedule</a> or you can send a message to inquire about the cancellation. <br><br>'
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



def email_body_review_reminder():
	""" generate email body (HTML).  Rate and review email, both buyer and seller; called from ht_send_review_reminder."""
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '\t<tr>td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px; padding-right:75px" align="left" valign="top">'
	msg = msg + '\t\t <font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">We hope you had a great appointment!<br>'
	msg = msg + '\t\t\t Your opinion goes a long way&mdash;write up your review of the appointment so others can learn from your experience with <a href="#" style="color:#1488CC">{user\'s name}</a></font><br><br>'
	msg = msg + '\t</td></tr>'

	msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:200px" align="left" valign="top">'
	msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #1488CC;font-size: 14px;border-radius: 3px;border: 1px solid #1488CC;font-family:Garamond, EB Garamond, Georgia, serif; width:100px;text-align:center;" target="_blank">Rate & Review</a>'
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



################################################################################
### PEER MESSAGES ##############################################################
################################################################################

def email_body_to_user_sending_msg(profile, message):
	""" generate email body (HTML).  When a user sends a message to a peer-user; send via ht_send_peer_message()."""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWay to get the conversation started! You messaged <a href=\"https://127.0.0.1:5000/profile?hero=' + profile.prof_id + '\" style="color:#e75f63">' + profile.prof_name.encode('utf8', 'ignore') + '</a> and should get a response soon.<br><br>\'\n</font>\n<br>\n</td>\n</tr>\n</table>' + footer'
	
	return msg




def email_body_to_user_receiving_msg(profile, message):
	""" generate email body (HTML).  When a user sends a message to a peer-user; sent via ht_send_peer_message()."""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou received a message from <a href=\"https://127.0.0.1:5000/profile?hero=' + str(profile.prof_id) + '\" style="color:#e75f63">' + profile.prof_name.encode('utf8', 'ignore') + '</a>. <br><br>\n<br>\n<i>' + message.msg_content + '</i>\n</font>\n<br>\n</td>\n</tr>\n</table>' + footer
	
	return msg









################################################################################
### BETA Welcome Message #######################################################
################################################################################


def email_body_beta_email(referral_code):
	""" HTML for sending the beta email """

	msg = header + '<table cellspacing=0 width=80% align=center>\n<tr>\n<td style=padding-top:50px;padding-bottom:10px align=left valign=top>\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">Thanks for signing up for Insprite! We are excited that you\'re interested in what we are doing over here. We are creating Insprite to be a vibrant, friendly community where you can both learn from creative people in your area, and teach your passions to others. We will be in touch when we\'re getting ready to launch -- tentatively in late 2014. We can\'t wait to show you what we\'ve been working on. You\'re going to love it.<br><br>\nIf you\'d like to tell us more about yourself, become a mentor, or if you want to help out in any other way, please just respond to this email -- we\'d love to hear from you.<br><br>\nFinally, if you know someone that might want to join our community, <strong>please share this personalized link</strong>, and we\'ll know you sent them!<br><br>Your referral link: <a href="http://www.insprite.co?ref='+referral_code+'" style=color:#1488CC>http://www.insprite.co?ref='+referral_code+'</a>\n<br><br>\nSpritely yours,<br>\nThe Insprite Gang\n</font>\n</td>\n</tr>\n</table>\n' + footer

	return msg