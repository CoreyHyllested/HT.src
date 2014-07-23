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
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
from server.email_body import *
from pprint import pprint as pp
import json, smtplib, urllib




def ht_email_welcome_message(user_email, user_name, challenge_hash):
	verify_email_url  = 'https://127.0.0.1:5000/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email)
	msg_text = "Welcome to Insprite!\n"
	msg_html = email_body_verify_account(verify_email_url)

	msg = create_msg('Welcome to Insprite', user_email, user_name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)




def ht_send_password_recovery_link(account):
	""" Emails the password recovery link to a user """
	url = 'https://127.0.0.1:5000/password/reset/' + str(account.sec_question) + "?email=" + str(account.email)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = email_body_recover_your_password(url)

	msg = create_msg('Reset your Insprite password', account.email, account.name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(account.email, msg)




def ht_send_password_changed_confirmation(user_email):
	""" email user 'password changed' confirmation notice. """
	msg_html = email_body_password_changed_confirmation('url')
	msg_text = None	# TODO	 #msg.attach(MIMEText(msg_html, 'plain'))

	msg = create_msg('Your Insprite password has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)



def ht_send_email_address_verify_link(email_address, account):
	print 'send a verify this email account to ' + str(email_address) + '\njust stubbed out'
	msg_html = email_body_verify_email_address('url')  #Bug
	msg_text = None	# TODO	 #msg.attach(MIMEText(msg_html, 'plain'))

	msg = create_msg('Verify your email address', email_address, account.name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)


def ht_send_email_address_changed_confirmation(user_email, new_email):
	""" email user 'email address changed' confirmation noticed. """
	msg_html = email_body_email_address_changed_confirmation('url', new_email)
	msg_text = None

	msg = create_msg('Your Insprite email address has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(user_email, msg)





################################################################################
### PROPOSAL | APPOINTMENT | MEETING EMAILS ####################################
################################################################################

def ht_send_meeting_proposed_notifications(proposal, sa, sp, ba, bp):
	ht_send_meeting_proposed_notification_to_sellr(proposal, sa.email, sp.prof_name.encode('utf8', 'ignore'), bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	ht_send_meeting_proposed_notification_to_buyer(proposal, ba.email, bp.prof_name.encode('utf8', 'ignore'), sp.prof_name.encode('utf8', 'ignore'), sp.prof_id)



def ht_send_meeting_proposed_notification_to_sellr(proposal, sellr_email, sellr_name, buyer_name, buyer_prof_id):
	print "ht_send_meeting_proposed_notification (to seller) (" + str(proposal.prop_uuid) + ") last touched by", str(proposal.prop_from)
	msg_html = email_body_new_proposal_notification_to_seller(proposal, buyer_name, buyer_prof_id)
	msg_subj = "Proposal to meet " + buyer_name
	if (proposal.prop_count > 1): msg_subj = msg_subj + " (updated)"

	msg = create_msg(msg_subj, sellr_email, sellr_name, 'noreply@insprite.co', u'Insprite Notifications')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(sellr_email, msg)



def ht_send_meeting_proposed_notification_to_buyer(proposal, buyer_email, buyer_name, sellr_name, sellr_prof_id):
	print "Proposal to hero (" + str(proposal.prop_uuid) + ") last touched by", str(proposal.prop_from)

	#msg_html = email_body_new_proposal_notification_to_buyer(sellr_name, proposal)
	#msg_subj = "Proposal to meet " + sellr_name
	#if (proposal.prop_count > 1): msg_subj = msg_subj + " (updated)"

	#msg = create_msg(msg_subj, buyer_email, buyer_name, 'noreply@insprite.co', u'Insprite Notifications')
	#msg.attach(MIMEText(msg_html, 'html'))
	#ht_send_email(buyer_email, msg)




def ht_send_meeting_rejected_notifications(proposal):
	""" email buyer (and seller?) the current proposal was rejected. """
	print 'ht_send_meeting_rejected_notifications enter'
	(sellr_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(proposal)
	sellr_profile = Profile.get_by_prof_id(proposal.prop_hero)
	buyer_profile = Profile.get_by_prof_id(proposal.prop_user)
	print 'ht_send_meeting_rejected_notifications create buyer_msg_html'
	buyer_msg_html = email_body_meeting_rejected_notification_to_buyer(proposal)
	print 'ht_send_meeting_rejected_notifications created buyer_msg_html'
	buyer_msg = create_msg(str(sellr_name) + ' rejected your proposal', buyer_email_addr, buyer_name, 'noreply@insprite.co', u'Insprite Notifications')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)

	print 'ht_send_meeting_rejected_notifications create sellr_msg_html'
	sellr_msg_html = email_body_meeting_rejected_notification_to_seller(proposal, buyer_profile.prof_name, buyer_profile.prof_id)
	print 'ht_send_meeting_rejected_notifications created sellr_msg_html'
	sellr_msg = create_msg('You rejected a proposal', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite Notifications')
	sellr_msg.attach(MIMEText(sellr_msg_html, 'plain'))
	ht_send_email(sellr_addr, sellr_msg)




def ht_send_meeting_accepted_notification(proposal):
	""" email proposal accepted emails to both buyer and seller."""
	(sellr_addr, sellr_name, buyer_addr, buyer_name) = get_proposal_email_info(proposal)
	sellr_profile = Profile.get_by_prof_id(proposal.prop_hero)
	buyer_profile = Profile.get_by_prof_id(proposal.prop_user)
	print 'sending proposal-accepted emails @ ' + proposal.get_prop_ts().strftime('%A, %b %d, %Y -- %H:%M %p')

	sellr_html = email_body_appointment_confirmation_for_seller(proposal, buyer_profile, sellr_profile)
	sellr_msg = create_msg('You accepted "' + user_name + 's proposal', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
	sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
	ht_send_email(sellr_addr, sellr_msg)

	# email buyer that seller accepted their proposal.
	buyer_html = email_body_appointment_confirmation_for_buyer(proposal, buyer_profile, sellr_profile)
	buyer_msg = create_msg(str(sellr_name) + ' accepted your proposal!', buyer_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
	ht_send_email(buyer_addr, buyer_msg)




def ht_send_meeting_canceled_notification(proposal):
	""" email notification to both buyer and seller, the appointment has been canceled."""
	(sellr_addr, sellr_name, buyer_addr, buyer_name) = get_proposal_email_info(proposal)

	# if canceled by seller.
		# only send meeting notice to buyer?
		#email_body_cancellation_from_seller_to_buyer():


	if (dt.utcnow() - proposal.prop_ts > timedelta(hours=48)):
		# assumes buyer canceled.
		sellr_html = email_body_cancellation_from_buyer_within_48_hours_to_seller()
	else:
		# assumes buyer canceled.
		sellr_html = email_body_cancellation_from_buyer_within_24_hours_to_seller()
	# email seller that meeting has been canceled.
	sellr_msg = create_msg('Meeting with ' + str(user_name) + ' canceled', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
	sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
	ht_send_email(sellr_addr, sellr_msg)

	# email buyer that meeting has been canceled.
	if (dt.utcnow() - proposal.prop_ts < timedelta(hours=24)):
		buyer_html = email_body_cancellation_from_buyer_within_24_hours()
	else:
		buyer_html = email_body_cancellation_from_buyer_outside_24_hours (buyer_name, sellr_name)
	buyer_msg = create_msg('Meeting with ' + str(sellr_name) + ' canceled', buyer_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
	ht_send_email(buyer_addr, buyer_msg)





################################################################################
### USER TO USER MESSAGES ######################################################
################################################################################

def ht_send_peer_message(send_profile, recv_profile, msg_subject, thread, message):
	try:
		recv_account = Account.get_by_uid(recv_profile.account)
		send_account = Account.get_by_uid(send_profile.account)
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (message.msg_flags & MSG_STATE_THRD_UPDATED):
		msg_subject = msg_subject + " (updated)"

	msg_to_recvr_html = email_body_to_user_receiving_msg(recv_profile, message)
	msg_to_recvr = create_msg(msg_subject, recv_account.email, recv_profile.prof_name, 'messages-'+str(message.msg_thread)+'@insprite.co', u'Insprite Messages')
	msg_to_recvr.attach(MIMEText(msg_to_recvr_html, 'html', 'UTF-8'))
	ht_send_email(recv_account.email, msg_to_recvr)

	msg_to_sendr_html = email_body_to_user_sending_msg(send_profile, message)
	msg_to_sendr = create_msg(msg_subject, send_account.email, send_profile.prof_name, 'messages-'+str(message.msg_thread)+'@insprite.co', u'Insprite Messages')
	msg_to_sendr.attach(MIMEText(msg_to_sendr_html, 'html', 'UTF-8'))
	ht_send_email(send_account.email, msg_to_sendr)





################################################################################
### DELAYED REMINDER EMAILS (Meeting, Review) ##################################
################################################################################

@mngr.task
def ht_send_meeting_reminder(user_email, user_name, prop_id):
	print 'ht_send_meeting_reminder() --  sending appointment reminder emails now for ' + prop_id
	proposal = Proposal.get_by_id(prop_uuid)

	# do nothing if canceled meeting
	if (proposal.canceled()): return

	msg_html = email_body_meeting_reminder()
	msg = create_notification('You Have an Appointment Tomorrow with {insert name}', user_email, user_name)
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)



@mngr.task
def ht_send_review_reminder(user_email, user_name, prop_uuid, review_id):
	print 'ht_send_review_reminder()  sending meeting review emails now for ' + prop_uuid
	proposal = Proposal.get_by_id(prop_uuid)
	if (proposal.canceled()):
		print 'ht_send_review_reminder() meeting was canceled.  Do not send reviews. ' + prop_uuid
		return

	(sellr_acct, sellr_prof) = get_account_and_profile(proposal.prop_hero)
	(buyer_acct, buyer_prof) = get_account_and_profile(proposal.prop_user)
	partner_prof = sellr_prof
	if (sellr_acct.email == user_email):
		partner_prof = buyer_prof

	msg_html = email_body_review_reminder()
	msg = create_notification('Review Meeting with ' + partner_prof.prof_name, user_email, user_name)
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(user_email, msg)





################################################################################
### HELPER and WORKHORSE FUNCTIONS #############################################
################################################################################

def get_proposal_email_info(proposal):
	(ha, hp) = get_account_and_profile(proposal.prop_hero)
	(ba, bp) = get_account_and_profile(proposal.prop_user)

	hero_addr = ha.email
	user_addr = ba.email
	hero_name = hp.prof_name.encode('utf8', 'ignore')
	user_name = bp.prof_name.encode('utf8', 'ignore')
	return (hero_addr, hero_name, user_addr, user_name)



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
	username = 'radnovic'
	password = "HeroTime"

	# open conn to SendGrid. Login send email.
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@herotime.co', email_addr, msg.as_string())
	s.quit()

