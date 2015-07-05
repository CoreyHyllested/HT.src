#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents. All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from email.header			import Header
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.models		 import *
from server.infrastructure.errors	import *
from server.infrastructure.basics	import *
from server.controllers.email_body	import *
from pprint import pprint as pp
import mandrill
import json, smtplib, urllib


email_client = mandrill.Mandrill('Fc1-NkxSROn715kzsldP8A')


def create_mandrill_message(template=None):
	message = {}

	# company details
	mvar_company		= 'Soulcrafting'
	mvar_description	= 'Trusted. Craftsmanship.'

	message['to'] = []
	message['template'] = template
	message['global_merge_vars'] =	[]
	message['global_merge_vars'].append({ 'name': 'LIST_COMPANY',		'content': mvar_company })
	message['global_merge_vars'].append({ 'name': 'LIST_DESCRIPTION',	'content': mvar_description })
	message['global_merge_vars'].append({ 'name': 'CONTACT_US',			'content': 'hello@soulcrafting.co'})
	return message


def email_team_notification(event, details):
	print event, '\n', details
	message = create_mandrill_message(template = 'sc-event')
	message['to'].append({'email': 'team@soulcrafting.co'})	#TODO
	message['global_merge_vars'].append({ 'name': 'EVENT',		'content': event})
	message['global_merge_vars'].append({ 'name': 'DETAILS',	'content': details})
	sc_send_mandrill_template(message)


def sc_email_welcome_message(user_email, user_name, challenge_hash):
	""" Emails the Welcome message, includes a 'verify your email' link."""
	verify_link = 'https://soulcrafting.co/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email)
	url_verify = 'https://soulcrafting.co/email/verify/' + str(challenge_hash) + "?email="+ urllib.quote_plus(user_email)

	message = create_mandrill_message(template = 'confirm-email')
	message['to'].append({'email': user_email})
	message['global_merge_vars'].append({ 'name': 'FNAME',			'content': user_name})
	message['global_merge_vars'].append({ 'name': 'VERIFY_EMAIL',	'content': url_verify})
	sc_send_mandrill_template(message)

	event	= 'New account'
	details	= 'Name: ' + str(user_name) + ' email: ' + str(user_email)
	email_team_notification(event, details)


def sc_send_password_recovery_link(account):
	""" Emails the password recovery link to a user """
	url_reset  = 'https://soulcrafting.co/password/reset/' + str(account.sec_question) + "?email=" + str(account.email)
	print 'https://127.0.0.1:5000/password/reset/' + str(account.sec_question) + "?email=" + str(account.email)

	message = create_mandrill_message(template = 'reset-password')
	message['to'].append({'email': account.email})
	message['global_merge_vars'].append({ 'name': 'FNAME',			'content': account.name})
	message['global_merge_vars'].append({ 'name': 'LINK_RESET',		'content': url_reset})

	sc_send_mandrill_template(message)


def sc_send_password_changed_confirmation(user_email):
	""" email user 'password changed' confirmation notice. """
	print 'sending password changed confirmation notice'
	message = create_mandrill_message(template = 'password-change-confirmation')
	message['to'].append({'email': user_email})
	sc_send_mandrill_template(message)


def sc_email_invite_friend(friend_email, friend_name, referral_id, gift_id=None):
	temp_friend	= str(friend_name)
	temp_invite	= str('https://soulcrafting.co/signup?ref=' + referral_id)
	temp_giftid	= str('https://soulcrafting.co/gift/'+gift_id)
	print str('https://127.0.0.1:5000/gift/'+gift_id)
	print str('https://127.0.0.1:5000/signup?ref='+referral_id)

	message = create_mandrill_message(template='invite-a-friend-html')
	message['to'].append({'email': friend_email})
	message['global_merge_vars'].append({ 'name': 'FNAME',			'content': temp_friend	})
	message['global_merge_vars'].append({ 'name': 'INVITE_LINK',	'content': temp_invite	})
	sc_send_mandrill_template(message)
	# maybe setup?


def sc_send_BR_email(prof_id, reference_email, brr):
	event	= 'New Reference Requested'
	profile = Profile.get_by_prof_id(prof_id)
	details	= str(prof_id) + ' (' + str(profile.prof_name) + ') wants a reference request sent to ' + str(reference_email)

	message = create_mandrill_message(template='write-fname-a-reference-on-soulcrafting')
	message['to'].append({'email': reference_email })
	message['global_merge_vars'].append({ 'name': 'FNAME',	'content': profile.prof_name })
	sc_send_mandrill_template(message)

	email_team_notification(event, details)


def sc_email_newproject_created(profile, project):
	event	= 'New project'
	details	= str(profile.prof_name) + ' (' + str(profile.prof_id) + ') created a new project ' + str(project.proj_name)
	email_team_notification(event, details)



def ht_send_email_address_verify_link(user_email, account):
	print 'send a verify this email account to ' + str(user_email)

	verify_email_url  = 'https://127.0.0.1:5000/email/verify/' + str(account.sec_question) + "?email="+ urllib.quote_plus(user_email)

	msg_html = email_body_verify_email_address('url', 'abcd')  #Bug
	msg_text = "Let's get your email address verified for your Insprite account.\n\nPlease copy and paste this security code into your settings: " + str(account.sec_question) + "\n\nOr, just click on this link: " + verify_email_url

	msg = create_msg('Verify your email address', user_email, account.name, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_text, 'plain' ))
	# msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(user_email, msg)



def ht_send_email_address_changed_confirmation(user_email, new_email):
	""" email user 'email address changed' confirmation noticed. """
	msg_html = email_body_email_address_changed_confirmation('url', new_email)
	msg_text = None

	msg = create_msg('Your Insprite email address has been updated', user_email, user_email, 'noreply@insprite.co', u'Insprite')
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(user_email, msg)



def	ht_send_share_email(email_addr, msg_sub, msg_body):
	""" A user is sharing SC with a friend. """
	msg_text = None

	print 'ht_send_share_email: sending email now'
	msg = create_msg(msg_sub, email_addr, email_addr, 'noreply@getsoulcrafting.com', u'Soulcrafting')
	msg.attach(MIMEText(msg_body, 'plain'))
#	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(email_addr, msg)





################################################################################
### PROPOSAL | APPOINTMENT | MEETING EMAILS ####################################
################################################################################

def ht_send_meeting_proposed_notifications(meeting, sa, sp, ba, bp):
	ht_send_meeting_proposed_notification_to_sellr(meeting, sa.email, sp.prof_name.encode('utf8', 'ignore'), bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	ht_send_meeting_proposed_notification_to_buyer(meeting, ba.email, bp.prof_name.encode('utf8', 'ignore'), sp.prof_name.encode('utf8', 'ignore'), sp.prof_id)



def ht_send_meeting_proposed_notification_to_sellr(meeting, sellr_email, sellr_name, buyer_name, buyer_prof_id):
	print "ht_send_meeting_proposed_notification_to_sellr: " + str(meeting.meet_id) + " last touched by", str(meeting.meet_owner)

	msg_html = email_body_new_proposal_notification_to_seller(meeting, buyer_name, buyer_prof_id)
	msg_subj = "Proposal to meet " + buyer_name
	if (meeting.meet_count > 1): msg_subj = msg_subj + " (updated)"

	msg = create_msg(msg_subj, sellr_email, sellr_name, 'noreply@insprite.co', u'Insprite Notifications')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(sellr_email, msg)



def ht_send_meeting_proposed_notification_to_buyer(meeting, buyer_email, buyer_name, sellr_name, sellr_prof_id):
	print "ht_send_meeting_proposed_notification_to_buyer: " + str(meeting.meet_id) + " last touched by", str(meeting.meet_owner)

	#msg_html = email_body_new_proposal_notification_to_buyer(sellr_name, meeting)
	#msg_subj = "Proposal to meet " + sellr_name
	#if (meeting.meet_count > 1): msg_subj = msg_subj + " (updated)"

	#msg = create_msg(msg_subj, buyer_email, buyer_name, 'noreply@insprite.co', u'Insprite Notifications')
	#msg.attach(MIMEText(msg_html, 'html'))
	#ht_send_email(buyer_email, msg)




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
		buyer_msg = create_notification(str(sellr_name) + ' rejected your proposal', buyer_email_addr, buyer_name)
		buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
		ht_send_email(buyer_email_addr, buyer_msg)

		print 'ht_send_meeting_rejected_notifications create sellr_msg_html'
		sellr_msg_html = email_body_meeting_rejected_notification_to_seller(meeting, buyer_profile.prof_name, buyer_profile.prof_id)
		print 'ht_send_meeting_rejected_notifications created sellr_msg_html'
		sellr_msg = create_notification('You rejected a proposal', sellr_email_addr, sellr_name)
		sellr_msg.attach(MIMEText(sellr_msg_html, 'plain'))
		ht_send_email(sellr_email_addr, sellr_msg)
	except Exception as e:
		# emails are not critical, swallow.
		ht_sanitize_error(e, reraise=False)




def ht_send_meeting_accepted_notification(meeting):
	""" email meeting accepted emails to both buyer and seller."""
	try:
		(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)
		sellr_profile = Profile.get_by_prof_id(meeting.meet_sellr)
		buyer_profile = Profile.get_by_prof_id(meeting.meet_buyer)

		sellr_html = email_body_appointment_confirmation_for_seller(meeting, buyer_profile, sellr_profile)
		sellr_msg = create_msg('You accepted ' + buyer_name + '\'s proposal', sellr_email_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
		sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
		ht_send_email(sellr_email_addr, sellr_msg)

		# email buyer that seller accepted their proposal.
		buyer_html = email_body_appointment_confirmation_for_buyer(meeting, buyer_profile, sellr_profile)
		buyer_msg = create_msg(str(sellr_name) + ' accepted your proposal!', buyer_email_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
		buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
		ht_send_email(buyer_email_addr, buyer_msg)
	except Exception as e:
		# emails are not critical, swallow.
		ht_sanitize_error(e, reraise=False)




def ht_send_meeting_canceled_notifications(meeting):
	""" send email notification to buyer and seller, appointment has been canceled."""
	print 'ht_send_meeting_canceled_notifications(' + meeting.meet_id + ')'

	try:
		(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)

		# if canceled by seller.
			# only send meeting notice to buyer?
			#email_body_cancellation_from_seller_to_buyer():


		print 'ht_send_meeting_canceled_notifications\t check if meeting occurs in 48 hours'
		# use tzinfo = None to remove timezone info, both are already in UTC.
		if ((dt.utcnow() - meeting.meet_ts.replace(tzinfo=None)) > timedelta(hours=48)):
			# assumes buyer canceled.
			print 'ht_send_meeting_canceled_notifications\t meeting occurs in more than 48 hours'
			sellr_html = email_body_cancellation_from_buyer_within_48_hours_to_seller(buyer_name)
		else:
			# assumes buyer canceled.
			print 'ht_send_meeting_canceled_notifications\t meeting occurs in less than than 48 hours'
			sellr_html = email_body_cancellation_from_buyer_within_24_hours_to_seller(buyer_name, str(meeting.meet_cost))

		# email seller that meeting has been canceled.
		print 'ht_send_meeting_canceled_notifications\t create seller_msg'
		sellr_msg = create_msg('Meeting with ' + str(buyer_name) + ' canceled', sellr_email_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
		sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
		ht_send_email(sellr_email_addr, sellr_msg)

		# email buyer that meeting has been canceled.
		print 'ht_send_meeting_canceled_notifications\t create buyer_path html'
		if (dt.utcnow() - meeting.meet_ts.replace(tzinfo=None) < timedelta(hours=24)):
			print 'ht_send_meeting_canceled_notifications\t meeting occurs in less than than 24 hours'
			buyer_html = email_body_cancellation_from_buyer_within_24_hours(sellr_name, str(meeting.meet_cost))
		else:
			print 'ht_send_meeting_canceled_notifications\t meeting occurs in > 24 hours'
			buyer_html = email_body_cancellation_from_buyer_outside_24_hours (buyer_name, sellr_name)
		print 'ht_send_meeting_canceled_notifications\t meeting create buyer_msg'
		buyer_msg = create_msg('Meeting with ' + str(sellr_name) + ' canceled', buyer_email_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
		buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
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
def ht_send_meeting_reminders(meet_id):
	print 'ht_send_meeting_reminders() --  sending appointment reminder emails now for ' + meet_id
	meeting = Meeting.get_by_id(meet_id)

	if (not meeting):
		print 'ht_send_meeting_reminders(' + str(meet_id) + ') doesn\'t exist'
		return

	if (meeting.canceled()):
		# meeting was canceled, log event and do not send reminder email.
		print 'ht_send_meeting_reminders() --  meetin canceled ' + meet_id
		return

	(sellr_email_addr, sellr_name, buyer_email_addr, buyer_name) = get_proposal_email_info(meeting)
	msg_html = email_body_meeting_reminder()

	msg_buyer = create_notification('You Have an Appointment Tomorrow with ' + sellr_name, buyer_email_addr, buyer_name)
	msg_buyer.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(buyer_email_addr, msg_buyer)

	msg_sellr = create_notification('You Have an Appointment Tomorrow with ' + buyer_name, sellr_email_addr, sellr_name)
	msg_sellr.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(sellr_email_addr, msg_sellr)




@mngr.task
def ht_send_review_reminder(user_email, user_name, meet_id, review_id):
	print 'ht_send_review_reminder()  sending meeting review emails now for ' + meet_id
	meeting = Meeting.get_by_id(meet_id)
	if (meeting.canceled()):
		print 'ht_send_review_reminder() meeting was canceled.  Do not send reviews. ' + meet_id
		return

	(sellr_acct, sellr_prof) = get_account_and_profile(meeting.meet_sellr)
	(buyer_acct, buyer_prof) = get_account_and_profile(meeting.meet_buyer)
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


def sc_send_mandrill_template(message):
	#send_template(self, template_name, template_content, message, async=False, ip_pool=None, send_at=None)
	content = []
	email_client.messages.send_template(message['template'], content, message)


def ht_send_email(email_addr, msg):
	# SendGrid login; TODO, move into config file.
	print 'ht_send_email: sending email now'
	username = 'cah'
	password = "passw0rd"

	# connect to SendGrid, login and send msg.
	#s = smtplib.SMTP('smtp.sendgrid.net', 587)
	#s.login(username, password)
	#s.sendmail('noreply@getsoulcrafting.com', email_addr, msg.as_string())
	#s.quit()

def ht_send_verification_to_list(account, email_set):
	print 'ht_send_verification_to_list() enter'
	try:
		account.reset_security_question()
		database.session.add(account)
		database.session.commit()
	except Exception as e:
		print type(e), e
		database.session.rollback()

	for email in email_set:
		print 'sending email to', email
		ht_send_email_address_verify_link(email, account)

