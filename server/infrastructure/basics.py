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
from server import ht_server
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from pprint import pprint as pp
import json, smtplib



def get_account_and_profile(profile_id):
	try:
		p = Profile.get_by_prof_id(profile_id)
		a = Account.get_by_uid(p.account)
	except Exception as e:
		print "Oh shit, caught error at get_account_and_profile" + e
		raise e
	return (a, p)




@mngr.task
def ht_charge_creditcard(prop_id, buyer_cc_token, buyer_cust_token, proposal_cost, prev_known_update_time=None):
	""" HT_charge_creditcard() captures money reserved. Basically, it charges the credit card. This is a big deal, don't fuck it up.
		ht_charge_creditcard() is delayed. That is why we must pass in prop_id, and get info from DB rather than pass in proposal.
	"""

	print 'ht_charge_creditcard: enter()'
	the_proposal = Proposal.get_by_id(prop_id)
	(ha, hp) = get_account_and_profile(the_proposal.prop_hero)	# hack, remove me...

	print 'ht_charge_creditcard: prop_id = ' + str(prop_id) + " for $" + str(proposal_cost)
	print 'ht_charge_creditcard: ' + str(the_proposal)


	if (the_proposal.prop_state != APPT_STATE_ACCEPTED):
		# update must set update_time. (if the_proposal.prop_updated > prev_known_update_time): corruption.
		print 'ht_charge_creditcard: proposal (' + the_proposal.prop_uuid + ') is not in ACCEPTED state(' + str(APPT_STATE_ACCEPTED) + '), in state ' + str(the_proposal.prop_state)
		return the_proposal.prop_state

	print 'ht_charge_creditcard:  proposal is reasonable, charge customer ' + the_proposal.charge_customer_id
	if (buyer_cust_token != the_proposal.charge_customer_id): print 'ht_charge_creditcard: WTF1.'

	try:
		s_prof = Profile.get_by_prof_id(the_proposal.prop_hero)
		o_auth = Oauth.get_stripe_by_uid(s_prof.account)
		if (o_auth is None): raise Exception ('user,' + str(ha.email) + ' doesnt have Stripe Connect Oauth')
		print 'ht_charge_creditcard: on behalf of ' +  s_prof.prof_name + ',' + o_auth.oa_secret
		charge = stripe.Charge.create (
			customer=buyer_cust_token,					# customer.id is the second one passed in
			capture=False,								# Do Not Capture now.  Capture later.
			amount=(the_proposal.prop_cost * 100),		# charged in pennies.
			currency='usd',
			description=the_proposal.prop_desc,
			application_fee=int((the_proposal.prop_cost * 7.1)-30),
			api_key=o_auth.oa_secret,
			receipt_email=ha.email
		)

		print 'ht_charge_creditcard: Post Charge'
		pp(charge)
		#print charge['customer']
		#print charge['captured']

		if charge['captured'] == True:
			print 'ht_charge_creditcard: Neeto -- but that shouldnt have happened'

		print 'ht_charge_creditcard: adding modified proposal'
		the_proposal.set_state(APPT_STATE_OCCURRED)				# TODO.  You should create the occurred_api. that charges first, then sets up reviews.  TOTAL HACK, REMOVE
		the_proposal.appt_charged = dt.now(timezone('UTC'))
		the_proposal.charge_transaction = charge['id']		 #once upon a time, this was the idea::the_proposal.charge_transaction = charge['balance_transaction']
		db_session.add(the_proposal)
		db_session.commit()
		print 'ht_charge_creditcard: successfully committed proposal'

	except StateTransitionError as ste:
		print 'ht_charge_creditcard: StateTransitionError', e
		db_session.rollback()
		raise e
	except Exception as e:
		#Cannot apply an application_fee when the key given is not a Stripe Connect OAuth key.
		print 'ht_charge_creditcard: Exception', type(e), e
		raise e

	captureTime = the_proposal.prop_tf + timedelta(days=2)
	captureTime = dt.now(timezone('UTC')) + timedelta(minutes=15)	#remove when done testing
	print 'ht_charge_creditcard: TODO... create mngr.event to capture in 4+days'
	ht_capture_creditcard.apply_async(args=[the_proposal.prop_uuid], eta=(captureTime))

	print 'ht_charge_creditcard: charge[failure_code] ' + str(charge['failure_code'])
	print 'ht_charge_creditcard: charge[balance_transaction] ' + str(charge['balance_transaction'])
	print 'ht_charge_creditcard: charge[failure_message] ' + str(charge['failure_message'])
	print 'ht_charge_creditcard: returning successful.'




@mngr.task
def ht_enable_reviews(prop_uuid):
	print 'ht_enable_reviews()  enter'
	proposal = Proposal.get_by_id(prop_uuid)
	(ha, hp) = get_account_and_profile(proposal.prop_hero)
	(ba, bp) = get_account_and_profile(proposal.prop_user)

	# if -- canceled --- do not create reviews.
	if (not proposal.accepted()):
		#TODO turn this into a Proposal method!
		print 'ht_enable_reviews(): ' +  proposal.prop_uuid + ' is not in ACCEPTED state =' + proposal.prop_state
		print 'ht_enable_reviews(): continuing; we might want to stop... depends on if we lost a race; prop implemnt OCCURRED_event'
		# check to see if reviews_enabled already [If it lost a race]
		# currently spaced it out (task-timeout pops 2 hours; dashboard-timeout must occur after 4)
		return

	review_hp = Review(proposal.prop_uuid, hp.prof_id, bp.prof_id)
	review_bp = Review(proposal.prop_uuid, bp.prof_id, hp.prof_id)
	print 'ht_enable_reviews()  review_hp: ' + str(review_hp.review_id)
	print 'ht_enable_reviews()  review_bp: ' + str(review_bp.review_id)

	try:
		db_session.add(review_hp)
		db_session.add(review_bp)
		db_session.commit()

		print 'ht_enable_reviews()  modify Proposal. Set state to OCCURRED.'
		proposal.review_user = review_bp.review_id
		proposal.review_hero = review_hp.review_id
		proposal.set_state(APPT_STATE_OCCURRED)
		db_session.add(proposal)
		db_session.commit()

		print 'ht_enable_reviews()  successfully created reviews, updated profile.  Disable in 30 + days.'
		review_start = proposal.prop_tf + timedelta(hours = 1)
		review_finsh = proposal.prop_tf + timedelta(days = 30)

		# Notifiy users.  Enqueue delayed review email.  TODO YET: Add an event notice on each users' dashboard.
		ht_send_review_reminder.apply_async(args=[ha.email, hp.prof_name, proposal.prop_uuid, review_bp.review_id], eta=review_start)
		ht_send_review_reminder.apply_async(args=[ba.email, bp.prof_name, proposal.prop_uuid, review_hp.review_id], eta=review_start)
		post_reviews.apply_async(args=[proposal.prop_uuid, review_hp.review_id, review_bp.review_id], eta=review_finsh)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	return None
