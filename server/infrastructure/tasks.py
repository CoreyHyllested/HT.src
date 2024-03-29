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
from server import sc_server
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
from server.controllers.email import *
from server.models	import *
from pprint import pprint as pp
from pytz import timezone
import json, smtplib
import stripe






def ht_meeting_create(values, uid):
	""" Create a PROPOSED Meeting. """

	print 'ht_meeting_create: enter()'
	#	Stripe fields should be validated.
	#	v1 - end time is reasonable (after start time)
	#	v2 - hero exists.
	#	v3 - place doesn't matter as much..
	#	v4 - cost..
	try:
		stripe_tokn = values.get('stripe_tokn')		# used to charge
		stripe_card = values.get('stripe_card')		# card to add to insprite_customer.
		stripe_cust = values.get('stripe_cust')
		#stripe_fngr = values.get('stripe_fngr')	#card_fingerprint

		prop_mentor = values.get('prop_mentor')
		prop_cost = values.get('prop_cost')
		prop_desc = values.get('prop_desc')
		prop_location = values.get('prop_location')
		prop_lesson = values.get('prop_lesson')
		prop_groupsize = values.get('prop_groupsize')

		print "ht_meeting_create: mentor:", prop_mentor
		print "ht_meeting_create: cost:", prop_cost
		print "ht_meeting_create: desc:", prop_desc
		print "ht_meeting_create: location:", prop_location
		print "ht_meeting_create: lesson:", prop_lesson
		print "ht_meeting_create: groupsize:", prop_groupsize

		# validate start/end times via conversion.
		prop_s_date = values.get('prop_s_date')
		prop_s_time = values.get('prop_s_time')
		prop_f_date = values.get('prop_f_date')
		prop_f_time = values.get('prop_f_time')
		dt_start = dt.strptime(prop_s_date  + " " + prop_s_time, '%A, %b %d, %Y %H:%M')
		dt_finsh = dt.strptime(prop_f_date  + " " + prop_f_time, '%A, %b %d, %Y %H:%M')

		# convert to user's local TimeZone.
		dt_start_pacific = timezone('US/Pacific').localize(dt_start)
		dt_finsh_pacific = timezone('US/Pacific').localize(dt_finsh)

		print 'ht_meeting_create: (from stripe) token =', stripe_tokn, 'card =', stripe_card
		hp	= Profile.get_by_prof_id(prop_mentor)
		bp	= Profile.get_by_uid(uid)
		ba  = Account.get_by_uid(uid)
		ha  = Account.get_by_uid(hp.account)
		stripe_cust  = ht_get_stripe_customer(ba, cc_token=stripe_tokn, cc_card=stripe_card, cust=stripe_cust)
		print 'ht_meeting_create: Mentee (' + str(bp.prof_name) + ', ' + str(stripe_cust) + ')'
		print 'ht_meeting_create: Mentor (' + str(hp.prof_name) + ')'

		meeting = Meeting(hp.prof_id, bp.prof_id, dt_start_pacific, dt_finsh_pacific, (int(prop_cost)/100), str(prop_location), str(prop_desc), str(prop_lesson), prop_groupsize, token=stripe_tokn, customer=stripe_cust, card=stripe_card)

		db_session.add(meeting)
		db_session.commit()
		print "ht_meeting_create: successfully committed meeting"
	except Exception as e:
		# IntegrityError, from commit()
		# SanitizedException(None), from Meeting.init()
		print type(e), e
		db_session.rollback()
		ht_sanitize_error(e)
	print "ht_meeting_create: sending notifications"
	ht_send_meeting_proposed_notifications(meeting, ha, hp, ba, bp)




def ht_meeting_update(meet_id, profile):
	meeting = meeting.get_by_id(meet_id)
	(ha, hp) = get_account_and_profile(meeting.meet_sellr)
	(ba, bp) = get_account_and_profile(meeting.meet_buyer)
	ht_send_meeting_proposed_notifications(meeting, ha, hp, ba, bp)




def ht_meeting_accept(meet_id, profile):
	print 'ht_meeting_accept(' + meet_id + ')'

	meeting = Meeting.get_by_id(meet_id)
	if (meeting is None): raise NoMeetingFound(meet_id)

	try:
		meeting.set_state(MeetingState.ACCEPTED, profile)
		db_session.add(meeting)
		db_session.commit()
	except Exception as e:
		# catches StateTransitionError
		# catches IntegrityError
		# catches TypeError, NameError
		db_session.rollback()
		ht_sanitize_error(e)

	try:
		print 'ht_meeting_accept: queue meeting reminder'
		remind_time = meeting.meet_ts - timedelta(days=2)
		(ha, hp) = get_account_and_profile(meeting.meet_sellr)
		(ba, bp) = get_account_and_profile(meeting.meet_buyer)

		print 'ht_meeting_accept: reminder emails @ ' + remind_time.strftime('%A, %b %d, %Y %H:%M %p')
		ht_send_meeting_reminders.apply_async(args=[meet_id], eta=remind_time)
	except Exception as e:
		print 'ht_meeting_accept: EXCEPTION', type(e), e
		ht_sanitize_error(e, reraise=False)

	ht_send_meeting_accepted_notification(meeting)
	return (200, 'Proposed meeting accepted')




def ht_meeting_cancel(meet_id, profile):
	print 'ht_meeting_cancel(' + str(meet_id) + ')'

	meeting = Meeting.get_by_id(meet_id)
	if (meeting is None): raise NoMeetingFound(meet_id)

	try:
		meeting.set_state(MeetingState.CANCELED, profile)
		db_session.add(meeting)
		db_session.commit()
	except Exception as e:
		# catches StateTransitionError
		db_session.rollback()
		ht_sanitize_error(e)

	ht_send_meeting_canceled_notifications(meeting)
	return (200, 'Proposed meeting canceled')




def ht_meeting_reject(meet_id, profile):
	print 'ht_meeting_reject(' +  str(meet_id) + ')', profile.prof_id

	meeting = Meeting.get_by_id(meet_id)
	if (meeting is None): raise NoMeetingFound(meet_id)

	try:
		meeting.set_state(MeetingState.REJECTED, profile)
		db_session.add(meeting)
		db_session.commit()
	except Exception as e:
		# catches StateTransitionError
		db_session.rollback()
		ht_sanitize_error(e)

	ht_send_meeting_rejected_notifications(meeting)
	return (200, 'Proposed meeting rejected')




def ht_get_stripe_customer(account, cc_token=None, cc_card=None, cust=None):
	""" returns Customer ID (cus_<HASH>); if customer doesn't exist, create Insprite Customer. """

	if (account.stripe_cust is not None):
		print 'ht_get_stripe_customer_id(): found customer', account.stripe_cust
		stripe.api_key = sc_server.config['STRIPE_SECRET']
		stripe_cust = stripe.Customer.retrieve(account.stripe_cust)
		print 'ht_get_stripe_customer_id(): update customer,' + str(stripe_cust.get('email')) + ', w/ info(' + str(cc_token) + ', ' + str(cc_card) + ')'
		stripe_cust.cards.create(card=cc_token)
		return account.stripe_cust

	print 'ht_get_stripe_customer_id: customer does not exist, create'
	try:
		stripe.api_key = sc_server.config['STRIPE_SECRET']

		ht_metadata = {}
		ht_metadata['ht_account'] = account.userid

		print 'ht_get_stripe_customer_id: customer info cc_token: ' + str(cc_token) + ' cc_card: ' + str(cc_card)
		stripe_customer = stripe.Customer.create(card=cc_token, description=str(account.userid), metadata=ht_metadata, email=account.email)
		stripe_cust	= stripe_customer['id']
		stripe_card	= stripe_customer['default_card']
		print 'ht_get_stripe_customer_id: New Customer (%s, %s)' % (stripe_cust, stripe_card)
		pp(stripe_cust)

		print 'ht_get_stripe_customer_id: Update Account'
		account.stripe_cust = stripe_cust
		db_session.add(account)
		db_session.commit()
	except Exception as e:
		# problems with customer create
		print type(e), e
		db_session.rollback()

	print 'ht_get_stripe_customer_id:', stripe_cust
	return stripe_cust





if __name__ != "__main__":
	print '@mngr.task... loading'
else:
	print "Whoa, this is main"
