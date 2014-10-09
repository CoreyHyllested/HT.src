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
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.models		 import *
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
from server.email_body import *
from pprint import pprint as pp
import json, smtplib, urllib

site_url = "https://127.0.0.1:5000"
# site_url = "https://www.insprite.co"

def ht_email_welcome_message(user_email, user_name, challenge_hash):
	verify_email_url  = 'https://127.0.0.1:5000/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email) + "&nexturl=dashboard"    
	msg_text = "Welcome to Insprite! We're thrilled that you've joined us.\n\nInsprite lets you connect with and learn from the creative people around you, and to teach your passions and skills to others. Please verify your email account by clicking this link " + verify_email_url + " before you start exploring the cool, creative experiences nearby.\n\nIf you are getting this message by mistake and did not create an account, email thegang@insprite.co and we will get on it ASAP.\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."     
	msg_html = email_body_verify_account(verify_email_url)

	msg = create_msg('Welcome to Insprite!', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)


def ht_send_mentor_welcome_message(user_email, user_name):
	new_session_url = "https://127.0.0.1:5000/session/new"
	msg_text = "Congrats! You\'re now an Insprite mentor.\nImpart your creative know-how in-person to those who want to learn from you&mdash;and get paid for it! Simply <a href='" + new_session_url + "''>create a session</a> if you haven\'t already, and let the community know what you can offer.\nQuestions? Learn more from our Become a Mentor FAQ or drop us a line at thegang@insprite.co.\nSpritely yours,\nThe Insprite Gang\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_html = email_body_mentor_welcome_message(new_session_url)

	msg = create_msg('Congrats! You\'re an Insprite mentor', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)

def ht_send_password_recovery_link(account):
	""" Emails the password recovery link to a user """
	url = 'https://127.0.0.1:5000/password/reset/' + str(account.sec_question) + "?email=" + str(account.email)
	msg_text = "Passwords can be tough to remember.\n\nNo biggie, simply follow the instructions at this link " + url + " to change it, and you'll be good to go.\n\nDid not request for a password reset? Email thegang@insprite.co ASAP.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_html = email_body_recover_your_password(url)

	msg = create_msg('Reset your Insprite password', account.email, account.name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(account.email, msg)




def ht_send_password_changed_confirmation(user_email):
	""" email user 'password changed' confirmation notice. """
	msg_html = email_body_password_changed_confirmation()
	msg_text = "We are sending you a reminder: You changed your password.\n\nWe want to keep your information safe and secure, so if you did not change it yourself email us at thegang@insprite.co ASAP and we will get on it.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."

	msg = create_msg('Your Insprite password has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)



def ht_send_email_address_verify_link(user_email, account, nexturl):
	""" sends a 'verify this email account' message to user """
	if (nexturl is None):
		nexturl = "settings"
	code = str(account.sec_question)
	verify_email_url  = 'https://127.0.0.1:5000/email/verify/' + code + "?email="+ urllib.quote_plus(user_email) + "&nexturl=" + nexturl
	msg_text = "Before you do certain things on Insprite, we ask that you verify your email address.\n\nPlease click on this link: " + verify_email_url + "\n\nIf you have trouble with the link, enter this security code into the verification box in Account Settings:\n\n" + code + "\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_html = email_body_verify_email_address(verify_email_url, code)  

	msg = create_msg('Verify your email address', user_email, account.name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(user_email, msg)


def ht_send_email_address_changed_confirmation(user_email, new_email):
	""" email user 'email address changed' confirmation noticed. """
	msg_html = email_body_email_address_changed_confirmation('url', new_email)
	msg_text = "We are sending you a reminder: You changed your email address.\n\nWe want to keep your information safe and secure, so if you did not change it yourself email us at thegang@insprite.co ASAP and we will get on it.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."


	msg = create_msg('Your Insprite email address has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(user_email, msg)





################################################################################
### MEETING EMAILS (PROPOSED/ACCEPTED/REJECTED/CANCELED) #######################
################################################################################

def ht_send_meeting_proposed_notifications(meeting, sa, sp, ba, bp):
	ht_send_meeting_proposed_notification_to_sellr(meeting, sa.email, sp.prof_name.encode('utf8', 'ignore'), bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	ht_send_meeting_proposed_notification_to_buyer(meeting, ba.email, bp.prof_name.encode('utf8', 'ignore'), sp.prof_name.encode('utf8', 'ignore'), sp.prof_id)


def ht_send_meeting_proposed_notification_to_sellr(meeting, sellr_email, sellr_name, buyer_name, buyer_prof_id):
	print "ht_send_meeting_proposed_notification_to_sellr: " + str(meeting.meet_id) + " last touched by", str(meeting.meet_owner)
	
	msg_html = email_body_new_proposal_notification_to_seller(meeting, buyer_name, buyer_prof_id)
	msg_text = "You received a session proposal from " + buyer_name + ".\n\nDate: " + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\nTime: " + meeting.get_meet_ts().strftime('%I:%M %p') + "--" + meeting.get_meet_tf().strftime('%I:%M %p') + "\nDuration: " + meeting.get_duration_in_hours() + "\nLocation: " + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription: " + meeting.get_description_html() + "\n\nTo accept the session, click here: " + meeting.accept_url() + "\n\nTo reject the session, click here: " + meeting.reject_url() + "\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_subj = "You've received a session proposal from " + buyer_name
	if (meeting.meet_count > 1): msg_subj = msg_subj + " (updated)"

	msg = create_msg(msg_subj, sellr_email, sellr_name, 'noreply@insprite.co', u'Insprite Notifications')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(sellr_email, msg)



def ht_send_meeting_proposed_notification_to_buyer(meeting, buyer_email, buyer_name, sellr_name, sellr_prof_id):
	print "ht_send_meeting_proposed_notification_to_buyer: " + str(meeting.meet_id) + " last touched by", str(meeting.meet_owner)

	msg_html = email_body_new_proposal_notification_to_buyer(meeting, sellr_name, sellr_prof_id)
	msg_text = "You sent a session proposal to " + sellr_name + ".\n\nDate:" + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\nTime:" + meeting.get_meet_ts().strftime('%I:%M %p') + '--' + meeting.get_meet_tf().strftime('%I:%M %p') + "\nDuration:" + meeting.get_duration_in_hours() + "\nLocation:" + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription:" + meeting.get_description_html() + "\nf\nStand by, and " + sellr_name + " will respond to your request soon.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_subj = "You sent " + sellr_name + " a session proposal"
	if (meeting.meet_count > 1): msg_subj = msg_subj + " (updated)"

	msg = create_msg(msg_subj, buyer_email, buyer_name, 'noreply@insprite.co', u'Insprite Notifications')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(buyer_email, msg)




def ht_send_meeting_rejected_notifications(meeting):
	""" email buyer (and seller?) the current proposed meeting was rejected. """
	print 'ht_send_meeting_rejected_notifications(' + meeting.meet_id + ')\t enter'
	try:
		# get user profiles, user names, and user email addresses
		(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)
		sellr_profile = Profile.get_by_prof_id(meeting.meet_sellr)
		buyer_profile = Profile.get_by_prof_id(meeting.meet_buyer)

		print 'ht_send_meeting_rejected_notifications create buyer_msg_html'
		buyer_msg_html = email_body_meeting_rejected_notification_to_buyer(meeting, sellr_name)
		buyer_msg_text = "" + sellr_name + " did not accept your session proposal this time around.\n\nWhy, you ask? There could be many reasons, but trust us, do not take it personally.\n<br><br>If you'd like, you can follow up with " + sellr_name + ".\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
		buyer_msg = create_notification(str(sellr_name) + ' rejected your session proposal', buyer_email_addr, buyer_name)
		buyer_msg.attach(MIMEText(buyer_msg_text, 'plain'))
		buyer_msg.attach(MIMEText(buyer_msg_html, 'html'))
		ht_send_email(buyer_email_addr, buyer_msg)

		print 'ht_send_meeting_rejected_notifications create sellr_msg_html'
		sellr_msg_html = email_body_meeting_rejected_notification_to_seller(meeting, buyer_profile.prof_name, meeting.meet_buyer)
		sellr_msg_text = "You did not accept a session proposal from " + buyer_name + "\n\nMessage " + buyer_name + " by clicking this link https://127.0.0.1:5000/profile?hero=" + buyer_profile.prof_id + " to see if you can work our a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
		print 'ht_send_meeting_rejected_notifications created sellr_msg_html'
		sellr_msg = create_notification('You rejected a session proposal', sellr_email_addr, sellr_name)
		sellr_msg.attach(MIMEText(sellr_msg_text, 'plain'))
		sellr_msg.attach(MIMEText(sellr_msg_html, 'html'))
		ht_send_email(sellr_email_addr, sellr_msg)
	except Exception as e:
		# emails are not critical, swallow.
		ht_sanitize_error(e, reraise=False)




def ht_send_meeting_accepted_notifications(meeting):
	""" email meeting accepted emails to both buyer and seller."""
	try:
		(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)
		sellr_profile = Profile.get_by_prof_id(meeting.meet_sellr)
		buyer_profile = Profile.get_by_prof_id(meeting.meet_buyer)

		sellr_msg_html = email_body_appointment_confirmation_for_seller(meeting, buyer_profile, sellr_profile)
		sellr_msg_text = "Fantastic! You\'ve accepted " + buyer_profile.prof_name + "\'s session proposal.\n\nDate: " + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\nTime: " + meeting.get_meet_ts().strftime('%I:%M %p') + "-" + meeting.get_meet_tf().strftime('%I:%M %p') + "\nDuration: " + meeting.get_duration_in_hours() + " hours\nLocation:" + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription: " + meeting.get_description_html() + "\n\nWe know life can be busy, so we will send you a reminder 24 hours in advance.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
		sellr_msg = create_msg('You accepted ' + buyer_name + '\'s session proposal', sellr_email_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
		sellr_msg.attach(MIMEText(sellr_msg_text, 'plain'))
		sellr_msg.attach(MIMEText(sellr_msg_html, 'html', 'UTF-8'))
		ht_send_email(sellr_email_addr, sellr_msg)

		# email buyer that seller accepted their proposal.
		buyer_msg_html = email_body_appointment_confirmation_for_buyer(meeting, buyer_profile, sellr_profile)
		buyer_msg_text = sellr_profile.prof_name + " accepted your session proposal!\n\nDate: " + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\nTime: " + meeting.get_meet_ts().strftime('%I:%M %p') + "-" + meeting.get_meet_tf().strftime('%I:%M %p') + "\nDuration:" + meeting.get_duration_in_hours() + " hours\nLocation:" + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription:" + meeting.get_description_html() + "\n\nWe know life can be busy, so we will send you a reminder 24 hours in advance.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
		buyer_msg = create_msg(str(sellr_name) + ' accepted your session proposal!', buyer_email_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
		buyer_msg.attach(MIMEText(buyer_msg_text, 'plain'))
		buyer_msg.attach(MIMEText(buyer_msg_html, 'html', 'UTF-8'))
		ht_send_email(buyer_email_addr, buyer_msg)
	except Exception as e:
		# emails are not critical, swallow.
		ht_sanitize_error(e, reraise=False)




def ht_send_meeting_canceled_notifications(meeting, profile):
	""" send email notification to buyer and seller, appointment has been canceled."""
	print 'ht_send_meeting_canceled_notifications(' + meeting.meet_id + '), canceled by ' + profile.prof_id

	try:
		(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)
		sellr_profile = Profile.get_by_prof_id(meeting.meet_sellr)
		buyer_profile = Profile.get_by_prof_id(meeting.meet_buyer)

		# Set this variable depending on if we are using a 24-hour or 48-hour cancellation window.
		window = 24

		if (profile.prof_id == meeting.meet_sellr):
			# The seller canceled.
			print 'ht_send_meeting_canceled_notifications\t seller canceled - create seller msg'
			
			sellr_msg_html = email_body_cancellation_from_seller_to_seller(buyer_profile)
			sellr_msg_text = "You canceled your upcoming session appointment with "+buyer_name+".\n\nYou can send them a message at https://127.0.0.1:5000/profile?hero=" + meeting.meet_buyer + " to see if you can work out a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."				

			buyer_msg_html = email_body_cancellation_from_seller_to_buyer(sellr_profile)
			buyer_msg_text = "Bummer - " + sellr_name + " canceled your upcoming session appointment.\n\nYou can send them a message at https://127.0.0.1:5000/profile?hero=" + meeting.meet_sellr + " to see if you can work out a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."			

		elif (profile.prof_id == meeting.meet_buyer):
			# The buyer canceled.

			# TODO - if canceled by buyer before acceptance. 
			# this one is sent to the buyer who just canceled.
			
			if (meeting.proposed()):
				print 'ht_send_meeting_canceled_notifications\t learner canceling before it was accepted.'

				# first write the seller email
				sellr_msg_html = email_body_cancellation_from_buyer_to_seller(buyer_profile)
				sellr_msg_text = buyer_name + " canceled his/her proposed session with you.\n\nNo further action is needed on your part.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."

				# now write the buyer email

				buyer_msg_html = email_body_cancellation_from_buyer_to_buyer_before_acceptance(sellr_profile)
				buyer_msg_text = "You canceled your proposed session with " + sellr_name + ".\n\nNeed to reschedule? Message the mentor at https://127.0.0.1:5000/profile?hero=" + meeting.meet_sellr + " to see if you can work out a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."

			else:
				print 'ht_send_meeting_canceled_notifications\t meeting not in the proposed state.'
				print 'ht_send_meeting_canceled_notifications\t check if meeting occurs within the window', str(window)
				
				# use tzinfo = None to remove timezone info, both are already in UTC.
				if ((dt.utcnow() - meeting.meet_ts.replace(tzinfo=None)) > timedelta(hours=window)):
					# this is within the allowed window, so no charges incurred.
					print 'ht_send_meeting_canceled_notifications\t meeting occurs in more than '+str(window)+' hours'

					# first write the seller email
					sellr_msg_html = email_body_cancellation_from_buyer_to_seller(buyer_profile)
					sellr_msg_text = buyer_name + " canceled his/her upcoming session with you.\n\nMessage " + buyer_name + " at https://127.0.0.1:5000/profile?hero=" + meeting.meet_buyer + " to see if you can work out a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."

					# now write the buyer email

					buyer_msg_text = "You canceled your session with " + sellr_name + ". You will not be charged for the cancellation.\n\nNeed to reschedule with " + sellr_name + "? Message them at https://127.0.0.1:5000/profile?hero=" + meeting.meet_sellr + " to see if you can work out a new date and time.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
					
					buyer_msg_html = email_body_cancellation_from_buyer_to_buyer(sellr_profile)

				else:
					# this is outside the cancellation window (within 24 or 48 hours of the session).
					print 'ht_send_meeting_canceled_notifications\t meeting occurs in less than than '+str(window)+' hours'
					
					# first write the seller email
					sellr_msg_html = email_body_late_cancellation_from_buyer_to_seller(buyer_profile, str(meeting.meet_cost), window)
					sellr_msg_text = "" + buyer_name + " canceled his/her upcoming session with you.\n\nSometimes things come up in life, but your time and talent are still valuable. You will receive $" + str(meeting.meet_cost) + " from " + buyer_name + " for the canceled booking, because it was canceled within " + str(window) + " hours of the session.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."

					# now write the buyer email
					buyer_msg_html = email_body_late_cancellation_from_buyer_to_buyer(sellr_profile, str(meeting.meet_cost), window)
					buyer_msg_text = "You canceled your session with " + sellr_name + ".\n\nWe know life can be busy, but we also value accountability and adhere to a " + str(window) + "-hour cancellation policy. You will be charged $" + str(meeting.meet_cost) + " for the session.\n\nQuestions? Drop us a line at thegang@insprite.co or read our Terms of Service and cancellation policies.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
				
		else:
			print "Uh oh, big problem. Person cancelling wasnt involved in the meeting."
			return
			
		# email seller that meeting has been canceled.		
		sellr_msg = create_msg('Session with ' + str(buyer_name) + ' has been canceled', sellr_email_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
		sellr_msg.attach(MIMEText(sellr_msg_text, 'plain'))
		sellr_msg.attach(MIMEText(sellr_msg_html, 'html', 'UTF-8'))
		ht_send_email(sellr_email_addr, sellr_msg)

		# email buyer that meeting has been canceled.
		buyer_msg = create_msg('Session with ' + str(sellr_name) + ' has been canceled', buyer_email_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
		buyer_msg.attach(MIMEText(buyer_msg_text, 'plain'))
		buyer_msg.attach(MIMEText(buyer_msg_html, 'html', 'UTF-8'))
		ht_send_email(buyer_email_addr, buyer_msg)			

	except Exception as e:
		# emails are not critical, swallow.
		ht_sanitize_error(e, reraise=False)




################################################################################
### USER TO USER MESSAGES ######################################################
################################################################################

def ht_send_peer_message(send_profile, recv_profile, msg_subject, thread, message):
	try:
		recv_account = Account.get_by_uid(recv_profile.account)
		send_account = Account.get_by_uid(send_profile.account)
	except Exception as e:
		print "ht_send_peer_message: Exception:", type(e), e
		db_session.rollback()

	if (message.msg_flags & MSG_STATE_THRD_UPDATED):
		msg_subject = msg_subject + " (updated)"

	messages_url = "https://127.0.0.1:5000/inbox"

	msg_to_recvr_html = email_body_to_user_receiving_msg(send_profile, message)
	msg_to_recvr_text = "You received a message from " + send_profile.prof_name.encode('utf8', 'ignore') + ".\n\n " + message.msg_content + "\n\nGo to your Insprite Inbox: " + messages_url + "\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_to_recvr = create_msg(msg_subject, recv_account.email, recv_profile.prof_name, 'messages-'+str(message.msg_thread)+'@insprite.co', u'Insprite Messages')
	msg_to_recvr.attach(MIMEText(msg_to_recvr_text, 'plain'))
	msg_to_recvr.attach(MIMEText(msg_to_recvr_html, 'html', 'UTF-8'))
	ht_send_email(recv_account.email, msg_to_recvr)

	# TODO - is this necessary or too spammy? Also, may not be 'starting a conversation' as implied in the text.
	msg_to_sendr_html = email_body_to_user_sending_msg(recv_profile, message)
	msg_to_sendr_text = "You messaged " + recv_profile.prof_name.encode('utf8', 'ignore') + " and should get a response soon.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_to_sendr = create_msg(msg_subject, send_account.email, send_profile.prof_name, 'messages-'+str(message.msg_thread)+'@insprite.co', u'Insprite Messages')
	msg_to_sendr.attach(MIMEText(msg_to_sendr_text, 'plain'))
	msg_to_sendr.attach(MIMEText(msg_to_sendr_html, 'html', 'UTF-8'))
	ht_send_email(send_account.email, msg_to_sendr)

	print "ht_send_peer_message: msg_to_recvr_text:", msg_to_recvr_text
	print "ht_send_peer_message: msg_to_sendr_text:", msg_to_sendr_text




################################################################################
### DELAYED REMINDER EMAILS (Meeting, Review) ##################################
################################################################################

@mngr.task
def ht_send_meeting_reminders(meet_id):
	print 'ht_send_meeting_reminders() --  sending appointment reminder emails now for ' + meet_id
	meeting = Meeting.get_by_id(meet_id)

	if (not meeting):
		print 'ht_send_meeting_reminders(' + str(meet_id) + ') doesn\'t exist'
		return

	if (meeting.canceled()):
		# meeting was canceled, log event and do not send reminder email.
		print 'ht_send_meeting_reminders() --  meeting canceled ' + meet_id
		return

	(sellr_acct, sellr_prof) = get_account_and_profile(meeting.meet_sellr)
	(buyer_acct, buyer_prof) = get_account_and_profile(meeting.meet_buyer)
	(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)

	msg_html_buyer = email_body_meeting_reminder(sellr_prof, meeting)
	msg_html_sellr = email_body_meeting_reminder(buyer_prof, meeting)
	msg_text_buyer = "You have a session with " + partner_prof.prof_name + " tomorrow.\n\nAs promised, we\'re sending you the details now so you don\'t have to worry about it later on.\n\nDate:" + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\n\nStart Time:" + meeting.get_meet_ts().strftime('%I:%M %p') + "\nDuration:" + meeting.get_duration_in_hours() + " hours\nLocation:" + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription:" + meeting.get_description_html() + "\n\nEnjoy!\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg_text_sellr = "You have a session with " + partner_prof.prof_name + " tomorrow.\n\nAs promised, we\'re sending you the details now so you don\'t have to worry about it later on.\n\nDate:" + meeting.get_meet_ts().strftime('%A, %b %d, %Y') + "\n\nStart Time:" + meeting.get_meet_ts().strftime('%I:%M %p') + "\nDuration:" + meeting.get_duration_in_hours() + " hours\nLocation:" + str(meeting.meet_location) + "\nTotal Cost: $" + str(meeting.meet_cost) + "\nDescription:" + meeting.get_description_html() + "\n\nEnjoy!\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	

	msg_buyer = create_notification('You have a session tomorrow with ' + sellr_name, buyer_email_addr, buyer_name)
	msg_buyer.attach(MIMEText(msg_text_buyer, 'plain'))
	msg_buyer.attach(MIMEText(msg_html_buyer, 'html', 'UTF-8'))
	ht_send_email(buyer_email_addr, msg_buyer)

	msg_sellr = create_notification('You have a session tomorrow with ' + buyer_name, sellr_email_addr, sellr_name)
	msg_sellr.attach(MIMEText(msg_text_sellr, 'plain'))
	msg_sellr.attach(MIMEText(msg_html_sellr, 'html', 'UTF-8'))
	ht_send_email(sellr_email_addr, msg_sellr)




@mngr.task
def ht_send_review_reminder(user_email, user_name, meet_id, review_id):
	print 'ht_send_review_reminder()  sending meeting review emails now for ' + meet_id

	# TODO - need a url to send them to.
	url = "/review/new/"+review_id

	meeting = Meeting.get_by_id(meet_id)
	if (meeting.canceled()):
		print 'ht_send_review_reminder() meeting was canceled.  Do not send reviews. ' + meet_id
		return

	(sellr_acct, sellr_prof) = get_account_and_profile(meeting.meet_sellr)
	(buyer_acct, buyer_prof) = get_account_and_profile(meeting.meet_buyer)
	partner_prof = sellr_prof
	if (sellr_acct.email == user_email):
		partner_prof = buyer_prof

	msg_html = email_body_review_reminder(url)
	msg_text = "We hope you had a great session with " +  partner_prof.prof_name + ".\n\nYour opinion goes a long way -- <a href=" + url + ">write a review</a> so others can learn from your experience.\n\n****************\n\nContact us at info@insprite.co\nSent by Insprite.co, Berkeley, California, USA."
	msg = create_notification('Review your session with ' + partner_prof.prof_name, user_email, user_name)
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)





################################################################################
### HELPER and WORKHORSE FUNCTIONS #############################################
################################################################################

def get_proposal_email_info(meeting):
	(ha, hp) = get_account_and_profile(meeting.meet_sellr)
	(ba, bp) = get_account_and_profile(meeting.meet_buyer)

	hero_addr = ha.email
	buyer_email_addr = ba.email
	sellr_name = hp.prof_name.encode('utf8', 'ignore')
	buyer_name = bp.prof_name.encode('utf8', 'ignore')
	return (hero_addr, sellr_name, buyer_email_addr, buyer_name)



def create_msg(subject, email_to, name_to, email_from, name_from):
	if (name_to == None):	name_to = email_to
	if (name_from == None):	name_from = email_from

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(name_to,	 'utf-8'), email_to)
	msg['From'] = "\"%s\" <%s>" % (Header(name_from, 'utf-8'), email_from)
	return msg



def create_notification(subject, email_to, name_to):
	if (name_to == None):	name_to = email_to

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(name_to,	 'utf-8'), email_to)
	msg['From'] = "\"%s\" <%s>" % (Header('Insprite Notifications', 'utf-8'), 'noreply@insprite.co')
	return msg



def ht_send_email(email_addr, msg):
	# SendGrid login; TODO, move into config file.
	print "ht_send_email: begin"
	username = 'radnovic'
	password = "HeroTime"

	# open conn to SendGrid. Login send email.
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@insprite.co', email_addr, msg.as_string())
	print "ht_send_email: email sent to", email_addr
	s.quit()

