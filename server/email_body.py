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

site_url = "https://127.0.0.1:5000"
# site_url = "https://www.insprite.co"

################################################################################
### ACCOUNT SETTINGS AND ADMINISTRATION ########################################
################################################################################

def email_body_verify_account(verify_email_url):
	""" HTML for verifying user account; called by ht_email_welcome_message() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWelcome to Insprite! We\'re thrilled that you\'ve joined us.<br><br>Insprite lets you connect with and learn from the creative people around you, and to teach your passions and skills to others. Please verify your email account before you start exploring the cool, creative experiences nearby.<br><br> If you are getting this message by mistake and did not create an account, <a href="mailto:thegang@insprite.co" style="color:#e75f63">let us know</a> and we will get on it ASAP.\n</font>\n</td>\n</tr>\n</table>\n<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:10px solid #fff;padding-top:0" align="center" valign="top">\n<a href="'+verify_email_url+'" style="color:#fff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:999em;margin-top:15px;margin-left:5px;font-family:Helvetica Neue,Arial,sans-serif" target="_blank">Verify your account</a>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_recover_your_password(url):
	""" HTML for sending the password recovery email; ht_send_password_recovery_link() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nPasswords can be tough to remember. No biggie, simply <a href="' + url + '" style="color:#e75f63">follow the instructions to change it</a> and you will be good to go.<br><br>\nDid not request for a password reset? <a href="mailto:thegang@insprite.co" style="color:#e75f63">Let us know ASAP</a>.</font>\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_password_changed_confirmation():
	""" HTML email body for updated password. sent via ht_send_password_changed_confirmation() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWe are sending you a reminder: You changed your password.<br><br>\nWe want to keep your information safe and secure, so if you did not change it yourself <a href="mailto:thegang@insprite.co" style="color:#e75f63">let us know ASAP</a> and we will get on it.\n</font>\n</td>\n</tr>\n</table>' + footer
	return msg
 

def email_body_verify_email_address(verify_email_url, code):  
	"""HTML for email address verification; sent via  ht_send_email_address_verify_link() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nBefore you do certain things on Insprite, we ask that you verify your email address. Please verify your account by clicking the button below.\n</font>\n</td>\n</tr>\n</table>\n<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:10px solid #fff;padding-top:0" align="center" valign="top">\n<a href="'+verify_email_url+'" style="color:#fff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:999em;margin-top:15px;margin-left:5px;font-family:Helvetica Neue,Arial,sans-serif" target="_blank">Verify your account</a>\n</td>\n</tr>\n</table>\n<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">If you have trouble with that link, enter this security code into the verification box in Account Settings:<br><br>' + code + '<br><br>\n</font>\n</td>\n</tr>\n</table>' + footer
	
	return msg



def email_body_email_address_changed_confirmation(url, new_email):
	"""HTML for email address change; sent via  ht_send_email_address_changed_confirmation() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWe are sending you a reminder: You changed your email.<br><br>\nWe want to keep your information safe and secure, so if you did not change it yourself <a href="mailto:thegang@insprite.co" style="color:#e75f63">let us know ASAP</a> and we will get on it.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


################################################################################
### PROPOSAL | APPOINTMENT | MEETING EMAILS ####################################
################################################################################

def email_send_meeting_proposed_notification_to_buyer(meeting, seller_name, sellr_profile):
	""" generate email body (HTML).  Buyer receives this email; sent via ht_send_meeting_proposed_notification_to_buyer. """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:16px">\nYou sent a lesson proposal to <a href="' + site_url + '/profile?hero=' + sellr_profile.prof_id + '" style="color:#e75f63">'+ sellr_name + '</a>. <br><br>\n<br>\n<b>Date: </b>' + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + '<br>\n<b>Time: </b>' + meeting.get_meet_ts().strftime('%I:%M %p') + '&mdash;' + meeting.get_meet_tf().strftime('%I:%M %p') + '<br>\n<b>Duration: </b>' + meeting.get_duration_in_hours() + '<br>\n<b>Location: </b>' + str(meeting.meet_location) + '<br>\n<b>Total Cost: </b> $' + str(meeting.meet_cost) + ' <br>\n<b>Description: </b> ' + meeting.get_description_html() + '\n<br><br>\nStand by, and <a href="' + site_url + '/profile?hero=' + sellr_profile.prof_id + '" style="color:#e75f63">'+ sellr_name + '</a> will respond to your request soon.</font>\n</td>\n</tr>\n</table>' + footer

	return msg

def email_body_new_proposal_notification_to_seller(meeting, buyer_name, buyer_prof_id):
	""" generate email body (HTML).  Notification when seller receives a new meeting proposal.  Sent via ht_send_sellr_proposal_update(). """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:16px">\nYou received a new lesson proposal from <a href="' + site_url + '/profile?hero=' + buyer_prof_id + '" style="color:#e75f63">'+ buyer_name + '</a>. <br><br>\n<br>\n<b>Date: </b>' + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + '<br>\n<b>Time: </b>' + meeting.get_meet_ts().strftime('%I:%M %p') + '&mdash;' + meeting.get_meet_tf().strftime('%I:%M %p') + '<br>\n<b>Duration: </b>' + meeting.get_duration_in_hours() + '<br>\n<b>Location: </b>' + str(meeting.meet_location) + '<br>\n<b>Total Cost: </b> $' + str(meeting.meet_cost) + ' <br>\n<b>Description: </b> ' + meeting.get_description_html() + '\n<br>\n</font>\n</td>\n</tr>\n<tr>\n<td style="background-color:#fff;border-top:0 solid #333;border-bottom:10px solid #fff;padding-top:10px" align="left" valign="top">\n<a href="'+ meeting.accept_url() +'" style="color:#fff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#29abe1;font-size:14px;border-radius:3px;border:1px solid #29abe1;font-family:Helvetica Neue,Arial,sans-serif;width:50px;text-align:center" target="_blank">Accept</a>\n<a href="'+ meeting.reject_url() +'" style="color:#fff;text-decoration:none;display:inline-block;min-height:38px;line-height:39px;padding-right:16px;padding-left:16px;background:#e55e62;font-size:14px;border-radius:3px;border:1px solid #e55e62;font-family:Helvetica Neue,Arial,sans-serif;width:50px;text-align:center" target="_blank">Reject</a>\n</td>\n</tr>\n</table>' + footer
	
	return msg


def email_body_meeting_rejected_notification_to_buyer(meeting, sellr_name):
	""" generate email body (HTML).  Buyer receives this email; sent via ht_send_meeting_rejected_notifications. """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px"><a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a> did not accept your lesson proposal this time around.<br><br>\nWhy, you ask? There could be many reasons, but trust us, do not take it personally.\n<br><br>Need to edit, manage or update the appointment? <a href="' + site_url + '/dashboard">Go for it</a>, or follow up with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg



def email_body_meeting_rejected_notification_to_seller(meeting, buyer_name, buyer_prof_id):
	""" generate email body (HTML).  Seller rejects proposal and receives this email; sent via ht_send_meeting_rejected_notifications. """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou did not accept a lesson proposal from <a href="' + site_url + '/profile?hero="' + buyer_prof_id + '" style="color:#e75f63">' + buyer_name + '</a><br>\nMessage <a href="' + site_url + '/profile?hero="' + buyer_prof_id + '" style="color:#e75f63">' + buyer_name + '</a> to see if you can work our a new date and time.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_appointment_confirmation_for_buyer(meeting, buyer_profile, sellr_profile, msg_url=site_url+"/message?profile=xxxx"):
	"""HTML email for buyer after the meeting proposal is accepted; called from ht_send_meeting_accepted_notification """
	msg = header +'<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:16px">\n<a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_profile.prof_name + '</a> accepted your lesson proposal.<br><br>\n<b>Date: </b>' + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + '<br>\n<b>Time: </b>' + meeting.get_meet_ts().strftime('%I:%M %p') + '&mdash;'+ meeting.get_meet_tf().strftime('%I:%M %p') +'<br>\n<b>Duration: </b> ' + meeting.get_duration_in_hours() + '<br>\n<b>Location: </b> ' + str(meeting.meet_location) + '<br>\n<b>Total Cost:</b> $' + str(meeting.meet_cost) + '<br>\n<br><br>\nNeed to edit, manage or update the appointment? <a href="' + site_url + '/dashboard" style="color:#e75f63">Go for it</a>, or send <a href="'+msg_url+'" style="color:#e75f63">' + sellr_profile.prof_name + '</a> a message.</font>\n</font>\n</td>\n</tr>\n</table>' + footer 
	
	return msg



def email_body_appointment_confirmation_for_seller(meeting, buyer_profile, sellr_profile, msg_user_link=site_url+"/message/USER"):
	"""HTML email for seller after accepted meeting proposal; called from ht_send_meeting_accepted_notification """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:16px">\nFantastic! You\'ve accepted <a href="' + site_url + '/profile?' + buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_profile.prof_name + '\'s lesson proposal</a>. <br><br>\n<b>Date:</b>' + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + '<br>\n<b>Time: </b>' + meeting.get_meet_ts().strftime('%I:%M %p') + '&mdash;'+ meeting.get_meet_tf().strftime('%I:%M %p') +'<br>\n<b>Duration:</b> ' + meeting.get_duration_in_hours() + '<br>\n<b>Location: </b> ' + str(meeting.meet_location) + '<br>\n<b>Total Cost: </b> $' + str(meeting.meet_cost) + '<br>\n<b>Description: </b> ' + meeting.get_description_html() + '\n<br><br>\nWe know life can be busy, so we will send you a reminder 24 hours in advance.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_cancellation_from_buyer_before_acceptance(buyer_name, sellr_name):
	""" generate email body (HTML).  The buyer cancels the appointment before seller accpets. sent via ht_send_meeting_canceled_notifications """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou cancelled your lesson with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>.<br><br>\nNeed to reschedule with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>? <a href="' + site_url + '/dashboard" style="color:#e75f63">Go for it</a>, or <a href="'+msg_url+'" style="color:#e75f63">send ' + sellr_profile.prof_name + ' a message</a>. <br><br>\n</font>\n</td>\n</tr>\n</table>' + footer
	
	return msg


def email_body_cancellation_from_buyer_outside_24_hours(buyer_name, sellr_name):
	""" generate email body (HTML).  The buyer cancels the appointment in advance of 24 hours threshold. sent via ht_send_meeting_canceled_notifications """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou cancelled your lesson with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>. You will not be charged for the cancellation. <br><br>\nNeed to reschedule with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>? <a href="' + site_url + '/dashboard" style="color:#e75f63">Go for it</a>, or <a href="'+msg_url+'" style="color:#e75f63">send ' + sellr_profile.prof_name + ' a message</a>. <br><br>\n</font>\n</td>\n</tr>\n</table>' + footer
	
	return msg



def email_body_cancellation_from_buyer_within_24_hours(sellr_name, cost):
	""" generate email body (HTML).  The buyer canceled the appointment within the 24 hours and will be charged.; sent via ht_send_meeting_canceled_notifications """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou cancelled your lesson with <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>.<br><br>\nWe know life can be busy, but we also value accountability and adhere to a 24-hour cancellation policy. You will be charged ' + str(meeting.meet_cost) + '</a> for the lesson.<br><br>\nQuestions? <a href="mailto:thegang@insprite.co" style="color:#e75f63">Drop us a line</a> or read up on our <a href="#" style="color:#e75f63">Terms of Service</a> and <a href="#" style="color:#e75f63">cancellation policies</a>.' + footer

	return msg



def email_body_cancellation_from_buyer_within_24_hours_to_seller(buyer_name, buyer_profile, cost):
	""" generate email body (HTML).  Buyer cancels the meeting within 24 hours and seller receives this email. sent via ht_send_meeting_canceled_notifications """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\n<a href="' + site_url + '/profile?' + buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_name + '</a> cancelled the lesson appointment.<br><br>\nSometimes things come up in life, but your time and talent are still valuable. You will receive ' + str(cost) +' from <a href="' + site_url + '/profile?' + buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_name + '</a> for the cancelled booking.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg



def email_body_cancellation_from_buyer_within_48_hours_to_seller(buyer_name, buyer_profile):
	""" generate email body (HTML).  Buyer cancels the meeting within 48 hours and seller receives this email.; ht_send_meeting_canceled_notifications """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\n<a href="' + site_url + '/profile?' + buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_name + '</a> cancelled the lesson appointment.<br><br>\nMessage <a href="' + site_url + '/profile?' + buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_name + '</a> to see if you can work out a new date and time.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg


def email_body_cancellation_from_seller_to_buyer(sellr_name, sellr_profile):
	""" generate email body (HTML).  Seller cancels the meeting, sends this email to buyer; sent via ht_send_meeting_canceled_notifications"""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\n<a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a> cancelled your lesson.<br><br>\nCheck out <a href="' + site_url + '/profile?'+ sellr_profile.prof_id + '" style="color:#e75f63">' + sellr_name + '</a>\'s availability, and send a new lesson proposal. (Sometimes, a little reshuffling can really make things happen.)\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg



def email_body_cancellation_from_seller(sellr_name, sellr_profile, buyer_name, buyer_profile):
	""" generate email body (HTML).  Seller cancels the meeting, sends this email to seller; sent via ht_send_meeting_canceled_notifications"""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\n You cancelled your lesson with <a href="' + site_url + '/profile?'+ buyer_profile.prof_id + '" style="color:#e75f63">' + buyer_name + '</a>.<br><br>\n</font>\n</td>\n</tr>\n</table>' + footer
	
	return msg


################################################################################
### DELAYED REMINDERS (MEETING, REVIEWS) #######################################
################################################################################

def email_body_meeting_reminder(partner_prof, meeting):
	""" generate email body (HTML). Both parties should receive 24 hours in advance of the meeting; sent by ht_send_meeting_reminder() """
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou have an lesson with <a href="' + site_url + '/profile?hero=' + partner_prof.prof_id + '" style="color:#e75f63">' + partner_prof.prof_name +'</a>tomorrow.<br><br>\nAs promised, we\'re sending you the details now so you don\'t have to worry about it later on.<br><br>\n<b>Date:</b>' + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + '<br>\n<b>Start Time:' + meeting.get_meet_ts().strftime('%I:%M %p') + '</b><br>\n<b>Duration:</b> ' + meeting.get_duration_in_hours() + ' hours<br>\n<b>Location:</b> ' + str(meeting.meet_location) + '<br>\n<b>Total Cost:</b> $' + str(meeting.meet_cost) + '<br>\n<b>Description:</b>' + meeting.get_description_html() + '<br><br>\nEnjoy!\n</font>\n</td>\n</tr>\n</table>' + footer
	
	return msg


def email_body_review_reminder(partner_prof, profile, url):
	""" generate email body (HTML).  Rate and review email, both buyer and seller; called from ht_send_review_reminder."""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nWe hope you had a great lesson with <a href="' + site_url + '/profile?hero=' + partner_prof.prof_id + '" style="color:#e75f63">' + partner_prof.prof_name + '</a>.<br>\n<br>\nYour opinion goes a long way&mdash;<a href="'+ url + '" style="color:#e75f63">write a review</a> so others can learn from your experience</a>.\n</font>\n</td>\n</tr>\n</table>' + footer

	return msg



################################################################################
### PEER MESSAGES ##############################################################
################################################################################

def email_body_to_user_sending_msg(profile, message):
	""" generate email body (HTML).  When a user sends a message to a peer-user; send via ht_send_peer_message()."""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou messaged <a href="' + site_url + '/profile?hero=' + profile.prof_id + '" style="color:#e75f63">' + profile.prof_name.encode('utf8', 'ignore') + '</a> and should get a response soon.\n</font>\n<br>\n</td>\n</tr>\n</table>' + footer
	
	return msg


def email_body_to_user_receiving_msg(profile, message):

	messages_url = site_url + "/inbox"

	""" generate email body (HTML).  When a user sends a message to a peer-user; sent via ht_send_peer_message()."""
	msg = header + '<table cellspacing="0" width="80%" align="center">\n<tr>\n<td style="padding-top:50px;padding-bottom:10px" align="left" valign="top">\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">\nYou received a message from <a href=\"' + site_url + '/profile?hero=' + str(profile.prof_id) + '" style="color:#e75f63">' + profile.prof_name.encode('utf8', 'ignore') + '</a>. <br><br><br>\n<i>' + message.msg_content + '</i>\n<br><br><br><a href="' + messages_url +'" style="color:#e75f63">Go to your Insprite Inbox</a>\n</font>\n<br>\n</td>\n</tr>\n</table>' + footer
	
	return msg


################################################################################
### BETA Welcome Message #######################################################
################################################################################


def email_body_beta_email(referral_code):
	""" HTML for sending the beta email """

	msg = header + '<table cellspacing=0 width=80% align=center>\n<tr>\n<td style=padding-top:50px;padding-bottom:10px align=left valign=top>\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">Thanks for signing up for Insprite! We are excited that you\'re interested in what we are doing over here. We are creating Insprite to be a vibrant, friendly community where you can both learn from creative people in your area, and teach your passions to others. We will be in touch when we\'re getting ready to launch -- tentatively in late 2014. We can\'t wait to show you what we\'ve been working on. You\'re going to love it.<br><br>\nIf you\'d like to tell us more about yourself, become a mentor, or if you want to help out in any other way, please just respond to this email -- we\'d love to hear from you.<br><br>\nFinally, if you know someone that might want to join our community, <strong>please share this personalized link</strong>, and we\'ll know you sent them!<br><br>Your referral link: <a href="http://www.insprite.co?ref='+referral_code+'" style=color:#e75f63">http://www.insprite.co?ref='+referral_code+'</a>\n<br><br>\nSpritely yours,<br>\nThe Insprite Gang\n</font>\n</td>\n</tr>\n</table>\n' + footer

	return msg


###############################################################################
### BETA Mentor Welcome Message ###############################################
###############################################################################


def email_body_mentor_welcome_message(new_lesson_url):
	""" HTML for sending the beta email to people who indicate they want to be mentors """

	msg = header + '<table cellspacing=0 width=80% align=center>\n<tr>\n<td style=padding-top:50px;padding-bottom:10px align=left valign=top>\n<font style="font-family:Helvetica Neue,Arial,sans-serif;color:#555;font-size:14px;line-height:14px">Congrats! You\'re now an Insprite mentor.<br><br>\nImpart your creative know-how in-person to those who want to learn from you&mdash;and get paid for it! Simply <a href="' + new_lesson_url + '">create a lesson</a> if you haven\'t already, and let the community know what you can offer.<br><br>\nQuestions? Learn more from our "Become a Mentor" FAQ or <a href="mailto:thegang@insprite.co" style=color:#e75f63">drop us a line</a> for more info.<br><br>\nSpritely yours,<br>\nThe Insprite Gang\n</font>\n</td>\n</tr>\n</table>\n' + footer

	return msg