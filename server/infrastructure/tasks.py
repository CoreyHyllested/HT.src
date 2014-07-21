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
from pytz import timezone
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
from server.email	import *
from sqlalchemy.exc import IntegrityError
from pprint import pprint as pp
import json, smtplib
import stripe



def ht_sanitize_errors(e, details=None):
	msg = 'caught error: ' + str(e)
	print msg
	if (type(e) == NoResourceFound):
		raise Sanitized_Exception(e, httpRC=400, msg=e.sanitized_msg())
	elif (type(e) == ValueError):
		raise Sanitized_Exception(e, httpRC=400, msg="Invalid input")
	elif (type(e) == StateTransitionError):
		raise Sanitized_Exception(e, httpRC=400, msg=e.sanitized_msg())
	else:
		raise e




def ht_proposal_create(values, uid):
	""" Creates a Proposal
		returns	on success: Proposal
		returns	on failure: Exception
	"""

	print 'ht_proposal_create: enter()'
	#	Stripe fields should be validated.
	#	v1 - end time is reasonable (after start time)
	#	v2 - hero exists.
	#	v3 - place doesn't matter as much..
	#	v4 - cost..
	try:
		print 'ht_proposal_create: validate input'
		stripe_tokn = values.get('stripe_tokn')		# used to charge
		stripe_card = values.get('stripe_card')		# card to add to insprite_customer.
		stripe_cust = values.get('stripe_cust')
		#stripe_fngr = values.get('stripe_fngr')	#card_fingerprint

		prop_hero = values.get('prop_hero')
		prop_cost = values.get('prop_cost')
		prop_desc = values.get('prop_desc')
		prop_place = values.get('prop_area')

		# validate start/end times via conversion.
		prop_s_date = values.get('prop_s_date')
		prop_s_hour = values.get('prop_s_hour')
		prop_f_date = values.get('prop_f_date')
		prop_f_hour = values.get('prop_f_hour')
		dt_start = dt.strptime(prop_s_date  + " " + prop_s_hour, '%A, %b %d, %Y %H:%M %p')
		dt_finsh = dt.strptime(prop_f_date  + " " + prop_f_hour, '%A, %b %d, %Y %H:%M %p')

		# convert to user's local TimeZone.
		dt_start_pacific = timezone('US/Pacific').localize(dt_start)
		dt_finsh_pacific = timezone('US/Pacific').localize(dt_finsh)
	except Exception as e:
		print type(e), e
		ht_sanitize_errors(e)

	print 'ht_proposal_create: (from stripe) token =', stripe_tokn, 'card =', stripe_card, 'cust =', stripe_cust

	try:
		# raises (No<Resrc>Found errors)
		hp	= Profile.get_by_prof_id(prop_hero)
		bp	= Profile.get_by_uid(uid)
		ba  = Account.get_by_uid(uid)
		ha  = Account.get_by_uid(hp.account)
		print 'ht_proposal_create: lookup buyer\'s stripe customer id'
		stripe_cust  = ht_get_stripe_customer(ba, cc_token=stripe_tokn, cc_card=stripe_card, cust=stripe_cust)
		print "ht_proposal_create:", bp.prof_name, ':', stripe_cust

		proposal = Proposal(hp.prof_id, bp.prof_id, dt_start_pacific, dt_finsh_pacific, (int(prop_cost)/100), str(prop_place), str(prop_desc), token=stripe_tokn, customer=stripe_cust, card=stripe_card)
		print "ht_proposal_create: successfully created proposal"
		db_session.add(proposal)
		db_session.commit()		 # raises IntegrityError
		print "ht_proposal_create: successfully committed proposal"

		ht_send_sellr_proposal_update_notification(proposal, ha.email, hp.prof_name.encode('utf8', 'ignore') , bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
		ht_send_buyer_proposal_update_notification(proposal, ba.email, bp.prof_name.encode('utf8', 'ignore') , hp.prof_name.encode('utf8', 'ignore'), hp.prof_id)
		print "ht_proposal_create: successfully emailed proposal information"
	except NoResourceFound as npf:
		ht_sanitize_errors(npf)
	except IntegrityError as ie:	#TODO: add to ht_sanitize
		db_session.rollback()
		ht_sanitize_errors(ie)
	except StateTransitionError as ste:
		db_session.rollback()
		ht_sanitize_errors(ste, details=500)
	except Exception as e:
		db_session.rollback()
		ht_sanitize_errors(e)
		print "ht_proposal_create: returning proposal"
	return proposal




def ht_proposal_update(p_uuid, p_from):
	prop = Proposal.get_by_id(p_uuid)
	(ha, hp) = get_account_and_profile(prop.prop_hero)
	(ba, bp) = get_account_and_profile(prop.prop_user)
	ht_send_sellr_proposal_update_notification(prop, ha.email, hp.prof_name.encode('utf8', 'ignore') , bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	ht_send_buyer_proposal_update_notification(prop, ba.email, bp.prof_name.encode('utf8', 'ignore') , hp.prof_name.encode('utf8', 'ignore'), hp.prof_id)




def ht_proposal_accept(prop_uuid, uid):
	print 'ht_proposal_accept()  enter; uuid :', prop_uuid
	try:
		the_proposal = Proposal.get_by_id(prop_uuid)
		stripe_card = the_proposal.charge_credit_card
		stripe_tokn = the_proposal.charge_user_token
		print 'ht_proposal_accept()  cust:', the_proposal.charge_customer_id, "  card:", stripe_card, "  token:", stripe_tokn 

		(ha, hp) = get_account_and_profile(the_proposal.prop_hero)
		(ba, bp) = get_account_and_profile(the_proposal.prop_user)

		# update proposal
		print 'ht_proposal_accept: change state to accepted'
		the_proposal.set_state(APPT_STATE_ACCEPTED, uid=uid)
		db_session.add(the_proposal)
		db_session.commit()

		print 'ht_proposal_accept: send confirmation notices'
		remindTime = the_proposal.prop_ts - timedelta(days=2)
		chargeTime = the_proposal.prop_ts - timedelta(days=2)
		reviewTime = the_proposal.prop_tf + timedelta(hours=2)	# so person can hit it up (maybe meeting runs long)
		print 'ht_proposal_accept: reminder emails @ ' + remindTime.strftime('%A, %b %d, %Y %H:%M %p')
		print 'ht_proposal_accept: charge the buyr @ ' + chargeTime.strftime('%A, %b %d, %Y %H:%M %p')
		print 'ht_proposal_accept: reviews sent @ ' + reviewTime.strftime('%A, %b %d, %Y %H:%M %p')

	except StateTransitionError as ste:
		print ste
		db_session.rollback()
		raise ste
	except NoResourceFound as nrf:
		print nrf
		db_session.rollback()
		raise nrf
	except Exception as e:
		print type(e), e
		db_session.rollback()
		raise e

	ht_send_meeting_accepted_notification(the_proposal)
	print 'ht_proposal_accept: queue events... reminder emails, enable_reviews.  Check to see if proposal was canceled.'
	enque_reminder1 = ht_email_meeting_reminder.apply_async(args=[ba.email, bp.prof_name, the_proposal.prop_uuid], eta=(remindTime))
	enque_reminder2 = ht_email_meeting_reminder.apply_async(args=[ha.email, hp.prof_name, the_proposal.prop_uuid], eta=(remindTime))

	# perhaps we should create a change_state event; ht_proposal_occrred.  which would check if it was canceled.  If not canceled; charge (+ queue capture) and enable Reviews
	ht_charge_creditcard.apply_async(args=[the_proposal.prop_uuid, ba.email, bp.prof_name.encode('utf8', 'ignore'), stripe_card, the_proposal.charge_customer_id, the_proposal.prop_cost], eta=chargeTime)
	ht_enable_reviews.apply_async(args=[the_proposal.prop_uuid], eta=(reviewTime))
	print 'ht_proposal_accept: returning successfully'





def ht_proposal_reject(prop_id, uid):
	print 'received proposal id:', prop_id
	bp = Profile.get_by_uid(uid)
	proposal = Proposal.get_by_id(prop_id)
	proposal.set_state(APPT_STATE_REJECTED, prof_id=bp.prof_id)

	try:
		db_session.add(proposal)
		db_session.commit()
	except Exception as e:
		db_session.rollback()
		print 'DB error:', e
		raise DB_Error(e, 'Shit that\'s embarrassing')
	ht_send_buyer_proposal_rejected_notification(proposal)
	return (200, 'success')





@mngr.task
def getDBCorey(x):
	print ('in getDBCorey' + str(x))
	accounts = Account.query.filter_by(email=('corey.hyllested@gmail.com')).all()
	print ('accounts = ' + str(len(accounts)))
	if (len(accounts) == 1):
		print str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)
	print 'exit getDBCorey'
	return str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)



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
		ht_email_review_notice.apply_async(args=[ha.email, hp.prof_name, proposal.prop_uuid, review_bp.review_id], eta=review_start)
		ht_email_review_notice.apply_async(args=[ba.email, bp.prof_name, proposal.prop_uuid, review_hp.review_id], eta=review_start)
		post_reviews.apply_async(args=[proposal.prop_uuid, review_hp.review_id, review_bp.review_id], eta=review_finsh)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	return None




@mngr.task
def post_reviews(prop_uuid, hp_review_id, bp_review_id):
	#30 days after enable, shut it down!
	proposal = Proposal.get_by_id(prop_uuid)
	proposal.set_state(APPT_STATE_COMPLETE)
	# get reviews.
	# mark incomplete reviews as incomplete.
	print 'post_reviews() -enter/exit'
	return None



@mngr.task
def ht_charge_creditcard(prop_id, buyer_email, buyer_name, buyer_cc_token, buyer_cust_token, proposal_cost, prev_known_update_time=None):
	""" HT_charge_creditcard() captures money reserved. Basically, it charges the credit card. This is a big deal, don't fuck it up.
		ht_charge_creditcard() is delayed. That is why we must pass in prop_id, and get info from DB rather than pass in proposal.
	"""

	print 'ht_charge_creditcard: enter()'
	the_proposal = Proposal.get_by_id(prop_id)
	(ha, hp) = get_account_and_profile(the_proposal.prop_hero)	# hack, remove me...

	print 'ht_charge_creditcard: prop_id = ' + str(prop_id) + " buyer =" + buyer_name + ',' + str(buyer_email) + " for $" + str(proposal_cost)
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
def ht_capture_creditcard(prop_id):
	""" HT_capture_cc() captures money reserved. Basically, it charges the credit card. This is a big deal, don't fuck it up.
		ht_capture_cc() is delayed. That is why we must pass in prop_id, and get info from DB rather than pass in proposal.
	"""
	print 'ht_capture_cc: enter()'
	proposal = Proposal.get_by_id(prop_id)
	(ha, hp) = get_account_and_profile(proposal.prop_hero)	# hack, remove me...

	print 'ht_capture_cc: prop_id = ' + str(prop_id) + ' for charge_id=' + str(proposal.charge_transaction)


	if (proposal.prop_state != APPT_STATE_OCCURRED): # and (proposal.test_flag(APPT_FLAG_MONEY_CAPTURED))):
		# update must set update_time. (if proposal.prop_updated > prev_known_update_time): corruption.
		print 'ht_capture_cc: proposal (' + proposal.prop_uuid + ') is not in OCCURRED state(' + str(APPT_STATE_OCCURRED) + '), in state ' + str(proposal.prop_state)
		#print 'ht_capture_cc: proposal (' + proposal.prop_uuid + ') didnt charge? funds yet'
		return proposal.prop_state

	try:
		print 'ht_capture_cc: initialize stripe with their Key() -- get o_auth'
		o_auth = Oauth.get_stripe_by_uid(hp.account)
		print 'ht_capture_cc: initialize stripe with their Key() -- o_auth.' + o_auth.oa_secret
		stripe.api_key = o_auth.oa_secret

		print 'ht_capture_cc: go get the charge'
		stripe_charge = stripe.Charge.retrieve(proposal.charge_transaction)

		print 'ht_capture_cc: initialize stripe with our Key() -- ready, set, capture'
		charge = stripe_charge.capture()

		print 'ht_capture_cc: Post Charge'
		pp(charge)

		if charge['captured'] == True:
			print 'ht_capture_cc: That\'s all folks, it worked!'

		proposal.set_flag(APPT_FLAG_MONEY_CAPTURED)
		proposal.appt_charged = dt.utcnow()  #appt_charged has no timezone, dumb, dumb, dumb
		print 'ht_capture_cc: keep the balance transaction? ' + str(charge['balance_transaction'])
		print 'ht_capture_cc: adding modified proposal'
		db_session.add(proposal)
		db_session.commit()
		print 'ht_capture_cc: successfully committed proposal'

	except StateTransitionError as ste:
		print 'ht_capture_cc: StateTransitionError', e
		db_session.rollback()
		raise e
	except Exception as e:
		#Cannot apply an application_fee when the key given is not a Stripe Connect OAuth key.
		print 'ht_capture_cc: Exception', type(e), e
		raise e

	print 'ht_capture_cc: charge[failure_code] = ' + str(charge['failure_code'])
	print 'ht_capture_cc: charge[balance_transaction] ' + str(charge['balance_transaction'])
	print 'ht_capture_cc: charge[failure_message] ' + str(charge['failure_message'])
	print 'ht_capture_cc: returning successful.'





def ht_get_stripe_customer(account, cc_token=None, cc_card=None, cust=None):

	print 'ht_get_stripe_customer_id(): enter'
	if (account.stripe_cust is not None):
		print 'ht_get_stripe_customer_id(): found!'
		return account.stripe_cust
		

	print 'ht_get_stripe_customer_id: customer does not exist, create'
	try:
		stripe.api_key = ht_server.config['STRIPE_SECRET']

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
