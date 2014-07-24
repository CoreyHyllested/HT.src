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
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
import json, urllib




def email_body_verify_account(verify_email_url):
	""" HTML for verifying user account; called by ht_email_welcome_message() """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#fffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
	msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px; padding-left:85px; padding-right:85px; padding-bottom:25px" align="left" valign="top">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Welcome to Insprite! We\'re thrilled that you\'ve joined us.<br><br>'
	msg = msg + 'Insprite lets you connect with and learn from the creative people around you, and to teach your passions and skills to others. We think you\'ll love exploring our growing community!<br><br>'
	msg = msg + 'Before you explore the cool things you can learn and experience from the inspiring, creative people around you (or decide to be one of them), <a href=\"' + verify_email_url + '\">please verify your email account</a> so we know you\'re a real breathing human.<br><br>'
	msg = msg + 'If you\'re getting this message by mistake and didn\'t create an account, <a href="mailto:thegang@insprite.co" style="color:#29abe1">drop us a line</a> and we\'ll get on it ASAP.</font>'
	msg = msg + '</td></tr>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600" height="200">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="center" valign="top">'
	msg = msg + '<a href="'+ verify_email_url + '" style="color:#ffffff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:999em;margin-top:15px;margin-left:5px;font-family:Garamond, EB Garamond, Georgia, serif;" target="_blank">Verify your account</a>'
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
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto:thegang@insprite.co" style="color:#29abe1">Contact Us</a> | Sent by <a href="https://insprite.co" style="color:#29abe1">Insprite</a>, California, USA. | <a href="#" style="color:#29abe1">Unsubscribe</a></font>'
	msg = msg + '</td></tr></table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600"><tr>'
	msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;" align="left" valign="middle">'
	msg = msg + '<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png"></td></tr></table>'
	return msg





def email_body_recover_your_password(url):
	""" HTML for sending the password recovery email; ht_send_password_recovery_link() """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="110" width="600" height="350">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:16px;">We get it&mdash;strong passwords can be tough to remember.<br><br>'
	msg = msg + 'No biggie, simply <a href=\"' + url + '\" style="color:#1488CC">follow the instructions to change it.</a> and you\'ll be good to go.<br><br>'
	msg = msg + 'Didn\'t request for a password reset?  <a href="mailto:thegang@insprite.co" style="color:#1488CC">Give us a holler ASAP</a>.</font>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 5px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/facebookIcon.png">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/twitterIcon.png">'
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
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto:thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
	msg = msg + '| Sent by <a href=\"https://insprite.co\">Insprite</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'
	return msg




def email_body_password_changed_confirmation(url):
	""" HTML email body for updated password. sent via ht_send_password_changed_confirmation() """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;" align="center" valign="middle">'
	msg = msg + '<img src="http://ryanfbaker.com/insprite/spacer-1.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:50px;" align="left" valign="top">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">We\'re just sending you a reminder: You changed your password.<br><br>'
	msg = msg + 'We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto:thegang@insprite.co" style="color:#1488CC">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

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
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:10px;"> <a href="mailto:thegang@insprite.co" style="color:#1488CC">Contact Us</a>'
	msg = msg + '| Sent by <a href="https://insprite.co" style="color:#1488CC">Insprite</a>, California, USA. | <a href="#" style="color:#1488CC">Unsubscribe</a></font>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr> <td style="border-top: 0px solid #333333; border-bottom: 0px solid #FFFFFF;">'
	msg = msg + '<img width="596px" src="http://ryanfbaker.com/insprite/footerImage.png">'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'
	return msg
 



def email_body_verify_email_address(url, code):  #bug267
	"""HTML for email address verification; sent via  ht_send_email_address_verify_link() """
	msg = ""
	return msg



def email_body_email_address_changed_confirmation(url, new_email):
	"""HTML for email address change; sent via  ht_send_email_address_changed_confirmation() """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
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
	msg = msg + '\t\t\t We want to keep your information safe and secure, so if you didn\'t change it yourself <a href="mailto:thegang@insprite.co" style="color:#1488CC">give us a holler ASAP</a> and we\'ll get on it.<br><br></font>'
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






################################################################################
### PROPOSAL | APPOINTMENT | MEETING EMAILS ####################################
################################################################################


def email_body_new_proposal_notification_to_seller(proposal, buyer_name, buyer_profile_id):
	""" generate email body (HTML).  Notification when seller receives a new proposal.  Sent via ht_send_sellr_proposal_update(). """
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
	msg = msg + '\n\t\t\t\tGreat! You received a new proposal from <a href=\"https://127.0.0.1:5000/profile?hero=' + buyer_profile_id + '\" style="color:#29abe1">'+ buyer_name + '</a>.'
	msg = msg + '\n\t\t\t\t<br><br><br>'
	msg = msg + '\n\t\t\t\tTime: ' + proposal.prop_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + proposal.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(proposal.prop_place) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(proposal.prop_cost) + '<br><br>'
	msg = msg + '\n\t\t\t\tDescription: ' + proposal.get_description_html() + '<br><br>'
	msg = msg + '\n\t\t\t</font><br><br>'
	msg = msg + '\n\t\t</td></tr>'

	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:150px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<a href=\"'+ proposal.accept_url() +'\" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #29abe1;font-size: 14px;border-radius: 3px;border: 1px solid #29abe1;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center;" target="_blank">Accept</a> '
	msg = msg + '\n\t\t\t<a href=\"'+ proposal.reject_url() +'\" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #e55e62;font-size: 14px;border-radius: 3px;border: 1px solid #e55e62;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center" target="_blank">Reject</a> '
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




def email_body_meeting_rejected_notification_to_buyer(proposal, sellr_name):
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




def email_body_meeting_rejected_notification_to_seller(proposal, buyer_name, buyer_prof_id):
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
	msg = msg + '\n\t\t\t\t\t\tYou did not accept a proposal from <a href=\"https://127.0.0.1:5000/profile?hero=\"' + buyer_prof_id + ' style="color:#29abe1">' + buyer_name + '</a>.<br><br>'
	msg = msg + '\n\t\t\t\t\t\tMessage <a href="#" style="color:#29abe1">' + buyer_name + '</a> to see if you can work our a new date and time.'
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


 


def email_body_appointment_confirmation_for_buyer(proposal, buyer_profile, sellr_profile, msg_url="https://127.0.0.1:5000/message?profile=xxxx"):
	"""HTML email for buyer after the proposal is accepted; called from ht_send_meeting_accepted_notification """
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
	msg = msg + '\n\t\t\t\tTime: ' + proposal.prop_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + proposal.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(proposal.prop_place) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(proposal.prop_cost) + '<br><br>'
	msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="'+msg_url+'" style="color:#1488CC">"' + sellr_profile.prof_name + '" a message.</a><br><br></font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://maps.googleapis.com/maps/api/staticmap?center='+proposal.prop_place+'&zoom=15&size=400x450&markers=size:large%8Ccolor:0xFFFF00%7Clabel:Insprite%7C'+proposal.prop_place+'">'
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




def email_body_appointment_confirmation_for_seller(proposal, buyer_profile, sellr_profile, msg_user_link='https://INSPRITE.co/message/USER'):
	"""HTML email for seller after accepted proposal; called from ht_send_meeting_accepted_notification """
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
	msg = msg + '\n\t\t\t\tTime: ' + proposal.prop_ts.strftime('%A, %b %d, %Y %H:%M %p') + '<br>'
	msg = msg + '\n\t\t\t\tDuration: ' + proposal.get_duration_in_hours() + ' hours<br>'
	msg = msg + '\n\t\t\t\tLocation: ' + str(proposal.prop_place) + '<br>'
	msg = msg + '\n\t\t\t\tFee: $' + str(proposal.prop_cost) + '<br><br>'
	msg = msg + '\t\t\t Need to edit, manage or update the appointment? <a href="https://127.0.0.1:5000/dashboard" style="color:#1488CC">Go for it</a>, or send <a href="' + msg_user_link + '" style="color:#1488CC"> ' + buyer_profile.prof_name + ' a message.</a><br><br>We know life can be busy, so we\'ll send you a reminder 24 hours in advance too.</font>'
	msg = msg + '\t</td></tr>'
	msg = msg + '</table>'

	msg = msg + '\n\t<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '\n\t\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '\n\t\t\t<img style="padding-right: 6px" src="http://maps.googleapis.com/maps/api/staticmap?center='+proposal.prop_place+'&zoom=15&size=400x450&markers=size:large%8Ccolor:0xFFFF00%7Clabel:Insprite%7C'+proposal.prop_place+'"><br>'
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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Shucks. You cancelled your appointment. Thanks for letting <a href="#" style="color:#29abe1">' + sellr_name + '</a> know ahead of time; you will not be charged for the cancellation.<br><br>'
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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> You cancelled the appointment with <a href="#" style="color:#29abe1">' + sellr_name + '</a>.<br><br>'
	msg = msg + '\t\t\t We know life can be busy, but we also value accountability within the community and adhere to a <a href="#" style="color:#29abe1">24-hour cancellation policy</a>. You will be charged <a href="#" style="color:#29abe1">$' + str(cost) + '</a> for the service. <br><br>'
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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> <a href="#" style="color:#29abe1"> ' + buyer_name + ' </a> cancelled your appointment.<br><br>'
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
	msg = msg + '\t\t<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;"> Drats. <a href="#" style="color:#29abe1">' + buyer_name + '</a> cancelled your appointment.<br><br>'
	msg = msg + '\t\t\t Message <a href="#" style="color:#29abe1">'+buyer_name+'</a> to see if you can work out a new date and time. </font><br><br>'
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



################################################################################
### PEER MESSAGES ##############################################################
################################################################################

def email_body_to_user_sending_msg(profile, message):
	""" generate email body (HTML).  When a user sends a message to a peer-user; send via ht_send_peer_message()."""
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="85" width="600" height="350">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;" align="left" valign="top">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">Way to get the conversation started! You messaged <a href=\"https://127.0.0.1:5000/profile?hero=' + profile.prof_id + '\" style="color:#29abe1">' + profile.prof_name.encode('utf8', 'ignore') + '</a> and should get a response soon.<br><br>'
	msg = msg + 'Until then, stand tight. <br><br>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

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
	return msg




def email_body_to_user_receiving_msg(profile, message):
	""" generate email body (HTML).  When a user sends a message to a peer-user; sent via ht_send_peer_message()."""
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ffffff"><tbody><tr>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #e6e6e6; border-bottom: 10px solid #FFFFFF; padding-top:75px; padding-left:58px" align="center" valign="middle">'
	msg = msg + '<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoA.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
	msg = msg + '</td></tr>'
	msg = msg + '</tbody>'
	msg = msg + '</table>'

	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6;" cellspacing="0" cellpadding="0" width="600">'
	msg = msg + '<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:0px;padding-left:75px" align="left" valign="top">'
	msg = msg + '<font style="font-family:Helvetica Neue;color:#555555;font-size:14px;">'
	msg = msg + 'You\'ve got mail. It\'s from <a href=\"https://127.0.0.1:5000/profile?hero=' + str(profile.prof_id) + '\" style="color:#29abe1">' + profile.prof_name.encode('utf8', 'ignore') + '</a>.'
	msg = msg + '<br><i>' + message.msg_content + '</i>'
	msg = msg + '</font><br>'
	msg = msg + '</td></tr>'
	msg = msg + '<td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF;padding-top:10px;padding-left:75px;padding-bottom:200px" align="left" valign="top">'
	msg = msg + '<a href="#" style="color:#ffffff;text-decoration: none;display: inline-block;min-height: 38px;line-height: 39px;padding-right: 16px;padding-left: 16px;background: #29abe1;font-size: 14px;border-radius: 3px;border: 1px solid #29abe1;font-family:Garamond, EB Garamond, Georgia, serif; width:50px;text-align:center;" target="_blank">Reply</a>'
	msg = msg + '</td></tr>'
	msg = msg + '</table>'

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
	return msg









################################################################################
### BETA Welcome Message #######################################################
################################################################################


def email_body_beta_email(url):
	""" HTML for sending the beta email """
	msg = '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr><td align="center" valign="top"></td></tr></tbody></table>'
	msg = msg + '<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#ebebeb"><tbody><tr>'
	msg = msg + '<table style="border-left: 2px solid #e6e6e6; border-right: 2px solid #e6e6e6; border-top: 2px solid #e6e6e6" cellspacing="0" cellpadding="10" width="600">'
	msg = msg + '<tbody>'

	msg = msg + '\t<tr><td style="background-color: #ffffff; border-top: 0px solid #333333; border-bottom: 10px solid #FFFFFF; padding-top:35px" align="center" valign="middle">'
	msg = msg + '\t\t<a href="https://insprite.co"><img src="http://ryanfbaker.com/insprite/inspriteLogoB.png" border="0" alt="Insprite" align="center" width="200px" height="55px" /></a>'
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

