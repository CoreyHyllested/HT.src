from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from server import ht_server
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.tasks_emails	 import *
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from server.infrastructure.basics		 import *
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
		returns	on failure: raised exception
	"""

	print 'ht_proposal_create: validate input'
	#	Stripe fields should be validated.
	#	v1 - end time is reasonable (after start time)
	#	v2 - hero exists.
	#	v3 - place doesn't matter as much..
	#	v4 - cost..
	try:
		stripe_tokn = values.get('stripe_tokn')
		stripe_card = values.get('stripe_card')
		stripe_cust = values.get('stripe_cust')
		stripe_fngr = values.get('stripe_fngr')	#card_fingerprint

		prop_hero = values.get('prop_hero')
		prop_cost = values.get('prop_cost')
		prop_desc = values.get('prop_desc')
		prop_place = values.get('prop_area')

		prop_s_date = values.get('prop_s_date')
		prop_s_hour = values.get('prop_s_hour')
		prop_f_date = values.get('prop_f_date')
		prop_f_hour = values.get('prop_f_hour')
		dt_start = dt.strptime(prop_s_date  + " " + prop_s_hour, '%A, %b %d, %Y %H:%M %p')
		dt_finsh = dt.strptime(prop_f_date  + " " + prop_f_hour, '%A, %b %d, %Y %H:%M %p')
	except Exception as e:
		print type(e), e
		ht_sanitize_errors(e)


	print 'token = ', stripe_tokn 
	print 'stripe_card = ', stripe_card 
	print 'stripe_cust = ', stripe_cust 
#	print 'updated_start = ', dt_start, '-', dt_finish

	try:
		# raises (No<Resrc>Found errors)
		hp	= Profile.get_by_prof_id(prop_hero)
		bp	= Profile.get_by_uid(uid)
		ba  = Account.get_by_uid(uid)
		ha  = Account.get_by_uid(hp.account)
		pi  = get_stripe_customer(uid=uid, cc_token=stripe_tokn, cc_card=stripe_card)
		print "PI = ", pi

		proposal = Proposal(str(hp.prof_id), str(bp.prof_id), dt_start, dt_finsh, (int(prop_cost)/100), str(prop_place), str(prop_desc), token=stripe_tokn, customer=pi, card=stripe_card)
		db_session.add(proposal)
		db_session.commit()		 # raises IntegrityError

		email_hero_proposal_updated(proposal, ha.email, hp.prof_name.encode('utf8', 'ignore') , bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
		email_user_proposal_updated(proposal, ba.email, bp.prof_name.encode('utf8', 'ignore') , hp.prof_name.encode('utf8', 'ignore'), hp.prof_id)
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
	return proposal




def ht_proposal_update(p_uuid, p_from):
	# send email to buyer.   (prop_from sent you a proposal).
	# send email to seller.  (proposal has been sent)

	prop = Proposal.get_by_id(p_uuid)
	(ha, hp) = get_account_and_profile(prop.prop_hero)
	(ba, bp) = get_account_and_profile(prop.prop_user)

	# pretty annoying.  we need to encode unicode here to utf8; decoding will fail.
	email_hero_proposal_updated(prop, ha.email, hp.prof_name.encode('utf8', 'ignore') , bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	email_user_proposal_updated(prop, ba.email, bp.prof_name.encode('utf8', 'ignore') , hp.prof_name.encode('utf8', 'ignore'), hp.prof_id)



def ht_proposal_accept(prop_id, uid):
	try:
		the_proposal = Proposal.get_by_id(prop_id, 'ht_appt_accept')
		stripe_card = the_proposal.charge_credit_card
		stripe_tokn = the_proposal.charge_user_token
		print 'ht_appointment_finailze() appt: ', prop_id, ", cust: ", the_proposal.charge_customer_id, ", card: ", stripe_card, ", token: ", stripe_tokn 

		# update proposal
		the_proposal.set_state(APPT_STATE_ACCEPTED, uid=uid)
		db_session.add(the_proposal)
		db_session.commit()

		print 'send confirmation notices to buyer and seller'
		(ha, hp) = get_account_and_profile(the_proposal.prop_hero)
		(ba, bp) = get_account_and_profile(the_proposal.prop_user)

		chargeTime = the_proposal.prop_ts - timedelta(days=1)
		remindTime = the_proposal.prop_tf - timedelta(days=2)

		print 'charge buyer @ ' + chargeTime.strftime('%A, %b %d, %Y %H:%M %p')
		print 'remind buyer @ ' + remindTime.strftime('%A, %b %d, %Y %H:%M %p')
		#send_appt_emails(ha.email, ba.email, the_proposal) TODO: this did take appointment as third field

		print 'calling ht_capturecard -- delayed'
		# add timestamp to ensure it hasn't been tampered with
		rc = ht_capture_creditcard(the_proposal.prop_uuid, ba.email, bp.prof_name.encode('utf8', 'ignore'), stripe_card, the_proposal.charge_customer_id, the_proposal.prop_cost, the_proposal.prop_updated) #, eta=chargeTime):

	except StateTransitionError as ste:
		print ste
		db_session.rollback()
		return (500, ste.sanitized_msg())
	except NoResourceFound as nrf:
		print nrf
		return (400, nrf.sanitized_msg())
	except Exception as e:
		print e
		db_session.rollback()
		return (500, e)

#	in reminder, check to see if it was canceled
#	enque_reminder1 = ht_send_reminder_email.apply_async(args=[sellr_a.email], eta=(remindTime))
#	enque_reminder2 = ht_send_reminder_email.apply_async(args=[buyer_a.email], eta=(remindTime))

	print 'returning from ht_appt_finalize', rc
	return (200, str(rc))




def ht_proposal_reject(p_uuid, uid):
	print 'received proposal uuid: ', p_uuid 
	committed = False
	bp = Profile.get_by_uid(uid)
	the_proposal = Proposal.get_by_id(p_uuid) 
	the_proposal.set_state(APPT_STATE_REJECTED, prof_id=bp.prof_id)

	try: # delete proposal 
		#TODO save these somewhere.
		db_session.add(the_proposal)
		db_session.commit()
		committed = True
	except Exception as e:
		db_session.rollback()
		print 'DB error:', e
		raise DB_Error(e, 'Shit that\'s embarrassing')
	send_proposal_reject_emails(the_proposal)
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




def enable_reviews(the_proposal):
	#is this submitted after stripe?  
	hp = the_proposal.prop_hero
	bp = the_proposal.prop_user

	print 'enable_reviews()'

	review_hp = Review(the_proposal.prop_uuid, hp, bp)
	review_bp = Review(the_proposal.prop_uuid, bp, hp)
	
	the_proposal.review_user = review_bp.review_id
	the_proposal.review_hero = review_hp.review_id
	#the_proposal.set_state(APPT_STATE_OCCURRED)

	try:
		db_session.add(review_hp)
		db_session.add(review_bp)
		db_session.commit()
		db_session.add(the_proposal)
		db_session.commit()

		# TODO create two events to send in 1 hr after meeting completion to do review
		# TODO send one event to disable the reviews in 1 month
	except Exception as e:
		db_session.rollback()
		print e	
	
	return None


@mngr.task
def disable_reviews(jsonObj):
	#30 days after enable, shut it down!
	#the_proposal.set_state(APPT_STATE_COMPLETE)
	print 'disable_reviews()'
	return None



@mngr.task
def ht_capture_creditcard(prop_id, buyer_email, buyer_name, buyer_cc_token, buyer_cust_token, proposal_cost, prev_known_update_time):
	#CAH TODO may want to add the Oauth_id to search and verify the cust_token isn't different
	print 'ht_capture_creditecard called: buyer_cust_token = ', buyer_cust_token, ", buyer_cc_token=", buyer_cc_token
	the_proposal = Proposal.get_by_id(prop_id, 'capture_cc')
	print the_proposal

	if (the_proposal.prop_state != APPT_STATE_ACCEPTED):
		trace (str(the_proposal.prop_uuid) + ' state is canceled (?, ' + str(the_proposal.prop_state) +  ')')
		print the_proposal.prop_uuid, ' state is canceled (?, ', the_proposal.prop_state ,')'
		return 'success, but state was canceld'

#	print str(the_appointment.updated)
#	print str(appointment.ts_begin)
#	print str(appointment.ts_finish)
	print str(the_proposal.charge_customer_id)

	try:
		charge = stripe.Charge.create (
			customer=buyer_cust_token, 	#		customer.id is the second one passed in
			#stripe_cust = Oauth(uid, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
			amount=(the_proposal.prop_cost * 100),
			currency='usd',
			description=the_proposal.prop_desc,
			#application_fee=int((the_appointment.cost * 7.1)-30),
			api_key="sk_test_nUrDwRPeXMJH6nEUA9NYdEJX"
					#if this key is an api_key -- i.e. someone's customer key -- e.g. the heros' customer key
			#-- subtracted stripe's fee?  -(30 +(ts.cost * 2.9)  
		)

		print 'That\'s all folks, it should have worked?'


		pp(charge)
		print 'Post Charge'
		print charge['customer']
		print charge['captured']
		print charge['balance_transaction']
		if charge['captured'] != True:
				print 'whoa'

		the_proposal.charge_transaction = charge['balance_transaction']
		the_proposal.set_state(APPT_STATE_CAPTURED)
		db_session.add(the_proposal)
		db_session.commit()
		#commie
	except StateTransitionError as ste:
		print e
		db_session.rollback()
	except Exception as e:
		#Cannot apply an application_fee when the key given is not a Stripe Connect OAuth key.
		print e
		return 'failed with ' + str(e)



#	Transaction 
	#transaction.timestamp = dt.utcnow()
	#transaction.timestamp = charge['id']  #charge ID
	#transaction.timestamp = charge['amount']  # same amount?
	#transaction.timestamp = charge['captured']  #True, right?
	#transaction.timestamp = charge['paid']  # == true, right?
	#transaction.timestamp = charge['livemode']  # == true, right?
	#transaction.timestamp = charge['balance_transaction']
	#transaction.timestamp = charge['card']['id']
	#transaction.timestamp = charge['card']['customer']
	#transaction.timestamp = charge['card']['fingerprint']


	#print charge['balance_transaction']
	print charge['failure_code']
	#print charge['failure_message']

	#queue two events to create review.  Need to create two addresses.
	print 'calling enable_reviews'
	enable_reviews(the_proposal)
	print 'returning out of charge'
	return 'Good -- becomes # when delayed'
	



def get_stripe_customer(uid=None, cc_token=None, cc_card=None):
	stripe.api_key = ht_server.config['STRIPE_SECRET']
	stripe_cust = None

	try:
		print 'check oauth for stripe account'
		stripe_cust = Oauth.get_stripe_by_uid(uid)
		print 'returned from oauth check'
		return stripe_cust.oa_account
	except NoOauthFound as nof:
		print 'customer does not exist, create'
		

	try:
		print 'create Customer w/ cc = ' + str(cc_token)
		stripe_cust_resp	= stripe.Customer.create(card=cc_token, description=str(uid))
		stripe_cust_userid	= stripe_cust_resp['id']
		stripe_card_dflt	= stripe_cust_resp['default_card']
		print stripe_cust_resp

		stripe_cust = Oauth(uid, OAUTH_STRIPE, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
		print stripe_cust
		db_session.add(stripe_cust)
		db_session.commit()
		print 'and ... saved HT/stripe cust to db'
	except UnboundLocalError as ule:
		print str(e)
		# raise ThisWasAlreadySubmitted (check back with RC. 
		# will need to grab asynch_submit RC -- stuff it in the appointment.
	except Exception as e:
		#problems with customer create
		print str(e)
		db_session.rollback()

	print 'return get_stripe_cust (', stripe_cust_userid, ')'
	return stripe_cust_userid

	

if __name__ != "__main__":
	print '@mngr.task... loading'
else:
	print "Whoa, this is main"
