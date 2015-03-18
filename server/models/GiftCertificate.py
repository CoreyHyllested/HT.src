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

from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.errors		 import *
from server.models	import Account, Profile, Oauth, Review
from server.email	import ht_send_review_reminder
from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm	import relationship, backref
from factory.fuzzy	import *
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime as dt, timedelta, tzinfo
from pytz	import timezone
from pprint	import pprint as pp
import uuid, factory, stripe



class CertificateState:
	RETURNED = -1	# returned.

	CREATED	= 0		# Created, paid for.
	PAIDFOR	= 1		# Paid for.
	CLAIMED = 2		# User claimed to their account.
	APPLIED = 3		# User applied discount to a project.
	DONE	= 4

	LOOKUP_TABLE = {
		RETURNED: 'RETURNED',
		CREATED : 'CREATED',
		PAIDFOR : 'PAIDFOR',
		CLAIMED : 'CLAIMED',
		APPLIED : 'APPLIED',
		DONE : 'REJECTED',
	}

	@staticmethod
	def state_name(state):
		return CertificateState.LOOKUP_TABLE.get(state, 'UNDEFINED')



################################################################################
### MEETING FLAGS FIELD ########################################################
################################################################################
################################################################################
## 	NAME				## BIT		## DETAILS
################################################################################
# Occurred flags.
################################################################################
GIFT_BIT_BUYER_REVIEWED =	12		# Buyer reviewed meeting
GIFT_BIT_SELLR_REVIEWED =	13		# Seller reviewed meeting
GIFT_BIT_MONEY_CAPTURED =	14		# Money has taken from user, 2 days after appt.
GIFT_BIT_MONEY_USERPAID =	15		# Appointment Captured money and Transferred payment to Seller.
GIFT_BIT_BUYER_CANCELED =	16		# Appointment was canceled by buyer.
################################################################################
### MEETING DETAILS ############################################################
################################################################################
GIFT_BIT_WAIVE_FEE		=	27		# Insprite is waiving its fee.
GIFT_BIT_RESPONSE		=	28		# Meeting went into negotiation.
GIFT_BIT_QUIET			=	29		# Meeting was quiet
GIFT_BIT_DIGITAL		=	30		# Meeting was digital
GIFT_BIT_RUNOVER		=	31
################################################################################

GIFT_FLAG_WAIVE_FEE			= (0x1 << GIFT_BIT_WAIVE_FEE)
GIFT_FLAG_MONEY_CAPTURED	= (0x1 << GIFT_BIT_MONEY_CAPTURED)




class GiftCertificate(Base):
	__tablename__ = "giftcertificate"
	gift_id		= Column(String(40), primary_key=True)													# NonSequential ID
	gift_state	= Column(Integer, nullable=False, default=CertificateState.CREATED)
	gift_value	= Column(Integer, nullable=False, default=0)											# Number of times vollied back and forth.
	gift_flags	= Column(Integer, nullable=False, default=0)											# Attributes: Quiet?, Digital?, Run-Over Enabled?

	gift_created = Column(DateTime(), nullable = False)
	gift_updated = Column(DateTime(), nullable = False)
	gift_charged = Column(DateTime())

	recipient_name = Column(String(64), nullable = False)
	recipient_mail = Column(String(64))
	recipient_cell = Column(String(16))
	recipient_addr = Column(String(128))										# THE PROFILE who can make a decision. (to accept, etc)
	recipient_note = Column(String(256))											# THE PROFILE who can make a decision. (to accept, etc)
	recipient_proj = Column(String(40), ForeignKey('project.proj_id'))
	recipient_prof = Column(String(40), ForeignKey('profile.prof_id'))			# THE PROFILE who can make a decision. (to accept, etc)

	gift_purchaser_paid = Column(Integer, default=0)		# Matches gift_value.
	gift_purchaser_name = Column(String(64))
	gift_purchaser_mail = Column(String(64))
	gift_purchaser_user	= Column(String(40), ForeignKey('profile.prof_id'), index=True)			# THE BUYER; requested hero.
	gift_purchaser_user	= Column(String(40), ForeignKey('profile.prof_id'), index=True)			# THE BUYER; requested hero.

	gift_stripe_customerid = Column(String(40)) #charge_customer_id	= Column(String(40), nullable = True)	# stripe customer id
	gift_stripe_creditcard = Column(String(40)) #charge_credit_card	= Column(String(40), nullable = True)	# stripe credit card
	gift_stripe_transaction = Column(String(40)) #charge_transaction	= Column(String(40), nullable = True)	# stripe transaction id
	gift_stripe_chargetoken = Column(String(40)) # charge_user_token	= Column(String(40), nullable = True)	# stripe charge tokn


	def __init__(self, recipient, purchaser, value=500, stripe_obj=None, token=None, customer=None, card=None, flags=None):
		self.gift_id	= str(uuid.uuid4())
		self.gift_state = CertificateState.PROPOSED
		self.gift_value = value
		self.gift_flags	= 0

		self.recipient_name = recipient.get('name')

		self.gift_stripe_customerid = customer
		self.gift_stripe_creditcard = card
#		self.gift_stripe_transaction = transaction
		self.gift_stripe_chargetoken = token

		if (token is None):		raise SanitizedException(None, user_msg = 'Meeting: stripe token is None')
		if (card is None):		raise SanitizedException(None, user_msg = 'Meeting: credit card is None')
		if (customer is None):	raise SanitizedException(None, user_msg = 'Meeting: customer is None')

		self.gift_created = dt.utcnow()
		self.gift_updated = dt.utcnow()
		self.gift_charged = dt.utcnow()
		#print 'GiftCertificate(p_uid=%s, cost=%s, location=%s)' % (self.gift_id, cost, location)


	def proposed(self): return (self.gift_state == CertificateState.PROPOSED)
	def accepted(self): return (self.gift_state == CertificateState.ACCEPTED)
	def occurred(self): return (self.gift_state == CertificateState.OCCURRED)
	def complete(self): return (self.gift_state == CertificateState.COMPLETE)
	def canceled(self): return (self.gift_state == CertificateState.CANCELED)


	def update(self, prof_updated, updated_s=None, updated_f=None, update_cost=None, updated_place=None, updated_desc=None, updated_state=None, updated_flags=None, updated_lesson=None, updated_groupsize=None): 
		self.gift_owner		= prof_updated
		self.gift_count		= self.gift_count + 1
		self.gift_updated	= dt.utcnow()

		if (updated_s is not None): self.gift_ts = updated_s
		if (updated_f is not None): self.gift_tf = updated_f
		if (updated_cost is not None):	self.gift_cost	= int(updated_cost)
		if (updated_desc is not None):	self.gift_details = updated_desc
		if (updated_place is not None):	self.gift_location = updated_place
		if (updated_state is not None):	self.gift_state = updated_state
		if (updated_flags is not None):	self.gift_flags = updated_flags
		if (updated_lesson is not None): 	self.gift_lesson = updated_lesson
		if (updated_groupsize is not None):	self.gift_groupsize = updated_groupsize


	@staticmethod
	def get_by_id(gift_id):
		meeting = None
		try: meeting = Meeting.query.filter_by(gift_id=gift_id).one()
		except NoResultFound as nrf: pass
		return meeting
	

	def set_flag(self, flag):
		self.gift_flags = (self.gift_flags | flag)

	def test_flag(self, flag):
		return (self.gift_flags & flag)

	def set_state(self, nxt_state, profile=None):
		cur_state = self.gift_state
		cstate_str = CertificateState.state_name(cur_state)
		nstate_str = CertificateState.state_name(nxt_state)

		transition_options = self.STATE_TRANSITION_MATRIX[cur_state]
		transition_process = transition_options.get(nxt_state)
		if (transition_process is None):
			raise StateTransitionError(self.__class__, self.gift_id, cur_state, nxt_state, self.gift_flags, user_msg='Meeting cannot perform that action')

		# attempt transition to next state, raising Exception if problem arises.
		print 'Meeting.set_state(' + nstate_str + ')'
		successful_transition = transition_process(self, profile, cur_state, nxt_state)
		if (successful_transition):
			self.gift_state = nxt_state
			self.gift_updated = dt.utcnow()
		return



	def get_gift_ts(self, tz=None):
		zone = self.gift_tz or 'US/Pacific'
		return self.gift_ts.astimezone(timezone(zone))

	def get_gift_tf(self, tz=None):
		zone = self.gift_tz or 'US/Pacific'
		return self.gift_tf.astimezone(timezone(zone))

	def get_duration(self):
		return (self.gift_tf - self.gift_ts)

	def get_duration_in_hours(self):
		td = self.gift_tf - self.gift_ts
		td_days = td.days
		td_hour	= (td.seconds / 3600)
		td_mins = (td.seconds % 3600) / 60

		elapsed	= ''
		if (td_hour > 1):
			elapsed = elapsed + str(td_hour) + ' hours'
		elif (td_hour == 1):
			elapsed = elapsed + str(td_hour) + ' hour'

		if (td_mins != 0):
			if (td_hour != 0): elapsed = elapsed + ' and '
			elapsed = elapsed + str(td_mins) + ' mins'
		return elapsed


	def get_description_html(self):
		description = self.gift_details.replace('\n', '<br>')
		return description
			

	def accept_url(self): return str('https://127.0.0.1:5000/meeting/accept?gift_id=' + self.gift_id)
	def reject_url(self): return str('https://127.0.0.1:5000/meeting/reject?gift_id=' + self.gift_id)
	def __repr__(self):	return '<meet %r, Hero=%r, Buy=%r, State=%r>' % (self.gift_id, self.gift_sellr, self.gift_buyer, self.gift_state)


	@property
	def serialize(self):
		return {
			'gift_id'		: self.gift_id,
			'gift_sellr'	: self.gift_sellr,
			'gift_buyer'	: self.gift_buyer,
			'gift_lesson'	: self.gift_lesson,
			'gift_groupsize': self.gift_groupsize,
			'gift_state'	: self.gift_state,
			'gift_flags'	: self.gift_flags,
			'gift_cost'		: self.gift_cost,
			'gift_updated'	: self.gift_updated.strftime('%A, %b %d, %Y %H:%M %p')
		}



	def __transition_proposed_to_accepted(self, profile, cur, nxt):
		if (self.gift_owner != profile.prof_id):
			print '\tOWNER - ', self.gift_owner, 'PERSON CHANGING meeting\t', profile.prof_id, profile.prof_name
			raise StateTransitionError(self.__class__, self.gift_id, cur, nxt, self.gift_flags, user_msg='Only meeting owner can perform that action')

		self.gift_secured = dt.utcnow()


		# if chargecc_time is 'in the past' (used during testing); set to five mins.
		chargecc_time = self.gift_ts.astimezone(timezone('UTC')) - timedelta(days=2)
		in_five_min = dt.now(timezone('UTC'))  + timedelta(minutes=2)
		if (in_five_min > chargecc_time): chargecc_time = in_five_min
		#print '\tMeeting.transition_PROPOSED_to_ACCEPTED(' + self.gift_id + ')\t@ ', chargecc_time.strftime('%A, %b %d, %Y %H:%M %p')

		# create event that will transition state and will charge the credit card
		meeting_event_chargecc.apply_async(args=[self.gift_id], eta=chargecc_time)
		return True



	def __transition_proposed_to_rejected(self, profile, cur, nxt):
		#print
		#print '\tMeeting.transition_PROPOSED_to_REJECTED()\tENTER\t', cur, nxt
		if (self.gift_owner != profile.prof_id):
			print '\tOWNER - ', self.gift_owner, 'PERSON CHANGING meeting\t', profile.prof_id, profile.prof_name
			raise StateTransitionError(self.__class__, self.gift_id, cur, nxt, self.gift_flags, user_msg='Only meeting owner can perform that action')

		# if (nxt == GIFT_STATE_TIMEDOUT): flags = self.set_flag(GIFT_BIT_TIMEDOUT)
		#print '\tMeeting.transition_PROPOSED_to_REJECTED()\tEXIT'
		return True


	def __transition_accepted_to_chargecc(self, profile, cur, nxt):
		print '\tMeeting.transition_ACCEPTED_to_CHARGECC()\tENTER'
		self.ht_charge_creditcard()

		# if review_time is 'in the past' (used during testing); set for five mins.
		review_time = self.gift_ts.astimezone(timezone('UTC')) + timedelta(hours=2)
		in_five_min = dt.now(timezone('UTC'))  + timedelta(minutes=2)
		if (in_five_min > review_time): review_time = in_five_min

		# create transition-state event; creates both review and capture events
		meeting_event_occurred.apply_async(args=[self.gift_id], eta=review_time)
		print '\tMeeting will transition to occurred @' + str(review_time.strftime('%A, %b %d, %Y %H:%M %p'))
		return True



	def __transition_chargecc_to_occurred(self, profile, cur, nxt):
		print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tENTER'
		#capture_time = self.gift_tf + timedelta(days=2)
		#capture_time = dt.now(timezone('UTC')) + timedelta(minutes=5)	#remove when done testing
		review_time	 = self.gift_tf.astimezone(timezone('UTC')) + timedelta(hours=2)
		in_five_min  = dt.now(timezone('UTC')) + timedelta(minutes=5)	#remove when done testing

		#if (capture_time < in_five_min):
		#	print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tcapture_time too soon, set to 5 min'
		#	review_time = in_five_min

		if (review_time < in_five_min):
			print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tReview_time too soon, set to 5 min'
			review_time = in_five_min

		print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tsend review @ ' + str(review_time.strftime('%A, %b %d, %Y %H:%M %p'))
		self.ht_capture_creditcard()
		ht_enable_reviews.apply_async(args=[self.gift_id], eta=review_time)
		return True


	def __transition_proposed_to_canceled(self, profile, cur, nxt):
		# Should this STATE-exist?  The Mentee tries to cancel.
		#print '\tMeeting.transition_PROPOSED_to_CANCELED()\tEXIT'
		return True

	def __transition_accepted_to_canceled(self, profile, cur, nxt):
		#print '\tMeeting.transition_ACCEPTED_to_CANCELED()\tENTER'
		return True

	def __transition_chargecc_to_canceled(self, profile, cur, nxt):
		#print '\tMeeting.transition_CHARGECC_to_CANCELED()\tENTER'
		return True


	def __transition_occurred_to_complete(self, profile, cur, nxt):
		# get reviews.
		# mark incomplete reviews as incomplete.
		return True

	def __transition_occurred_to_disputed(self, profile, cur, nxt):
		return True

	def __transition_complete_to_disputed(self, profile, cur, nxt):
		return True

	def __transition_disputed_to_resolved(self, profile, cur, nxt):
		return True


	STATE_TRANSITION_MATRIX =	{	CertificateState.PROPOSED	: { CertificateState.ACCEPTED	: __transition_proposed_to_accepted,
																CertificateState.REJECTED	: __transition_proposed_to_rejected,
																CertificateState.TIMEDOUT	: __transition_proposed_to_rejected,
																CertificateState.CANCELED	: __transition_proposed_to_canceled, },
									CertificateState.ACCEPTED	: { CertificateState.CHARGECC	: __transition_accepted_to_chargecc,
																CertificateState.CANCELED	: __transition_accepted_to_canceled, },
									CertificateState.CHARGECC	: { CertificateState.OCCURRED	: __transition_chargecc_to_occurred,
																CertificateState.CANCELED	: __transition_chargecc_to_canceled, },
									CertificateState.OCCURRED	: { CertificateState.COMPLETE	: __transition_occurred_to_complete,
																CertificateState.DISPUTED	: __transition_occurred_to_disputed, },
									CertificateState.COMPLETE	: { CertificateState.DISPUTED	: __transition_complete_to_disputed, },
									CertificateState.DISPUTED	: { CertificateState.DISPUTED	: __transition_disputed_to_resolved, },
								}


	def ht_charge_creditcard(self):
		print 'ht_charge_creditcard: enter (' + self.gift_id + ', ' + str(self.gift_state) + ', ' + str(self.gift_details[:20]) + ')  for $' + str(self.gift_cost)

		if (not self.accepted()):
			raise StateTransitionError(self.__class__, self.gift_id, self.gift_state, GIFT_STATE_CHARGECC, self.gift_flags, user_msg='Currently cannot perform that action')

		try:
			buyer_profile = Profile.get_by_prof_id(self.gift_buyer)
			sellr_profile = Profile.get_by_prof_id(self.gift_sellr)
			sellr_account = Account.get_by_uid(sellr_profile.account)
			o_auth = Oauth.get_stripe_by_uid(sellr_profile.account)
			if (o_auth is None): raise NoOauthFound(sellr_profile.account)

			print 'ht_charge_creditcard: seller (' + str(sellr_profile.prof_name) + ', ' + str(o_auth.oa_secret) + ')'
			print 'ht_charge_creditcard: buyer  (' + str(buyer_profile.prof_name) + ', ' + str(self.charge_customer_id) + ')'

			fee = 0
			if (self.gift_cost > 5 and not self.test_flag(GIFT_FLAG_WAIVE_FEE)):
				fee = int((self.gift_cost * 7.1)-30)

			print 'ht_charge_creditcard: cost (pennies)  ' +  str(self.gift_cost * 100)
			print 'ht_charge_creditcard: application fee ' +  str(fee)
			print 'ht_charge_creditcard: email_address   ' +  str(sellr_account.email)
			print 'ht_charge_creditcard: create token'
			token = stripe.Token.create(
				customer=self.charge_customer_id,		# customer.id is the second one passed in
				card=self.charge_credit_card,
				api_key=str(o_auth.oa_secret),
			)

			print 'ht_charge_creditcard: created token, create charge'
			charge = stripe.Charge.create(
				amount=(self.gift_cost * 100),			# charged in pennies.
				card=token,
				currency='usd',
				capture=False,							# Capture later.
				description=self.gift_details,
				application_fee=fee,
				api_key=str(o_auth.oa_secret),
				receipt_email=str(sellr_account.email)
#				statement_description='Insprite.co',
			)

			pp(charge)

			print 'ht_charge_creditcard: modify meeting'
			self.gift_charged = dt.now(timezone('UTC'))
			self.charge_transaction = charge['id']		 #once upon a time, this was the idea::proposal.charge_transaction = charge['balance_transaction']

			#print 'ht_charge-post: review_time will be ', self.get_gift_ts()  works
			#print 'committed-post: review_time will be ', self.get_gift_ts() #fails

			print 'ht_charge_creditcard: successfully committed meeting'
		except Exception as e:
			# cannot apply application_fee if fee is negative
			# cannot apply application_fee if the given key is not a StripeConnect
			print 'ht_charge_creditcard: Exception', type(e), e
			print 'ht_charge_creditcard: charge.failure_code =' + str(charge.get('failure_code')) + ', failure_message=' + str(charge.get('failure_message'))
			dump_error(e)
			ht_sanitize_error(e)



	def ht_capture_creditcard(self):
		""" HT_capture_cc() captures money reserved. Basically, it charges the credit card. This is a big deal, don't fuck it up.
			ht_capture_cc() is delayed. That is why we must pass in gift_id, and get info from DB rather than pass in proposal.
		"""
		print 'ht_capture_cc: enter(' + self.gift_id + ')'
		sellr_prof = Profile.get_by_prof_id(self.gift_sellr)
		print 'ht_capture_cc: charge_id=' + str(self.charge_transaction)

		# Meeting must be in this CHARGECC state to have this method be called get called
		#if (self.gift_state != CertificateState.CHARGECC): # and (self.test_flag(GIFT_BIT_MONEY_CAPTURED))):
		#	# update must set update_time. (if self.gift_updated > prev_known_update_time): corruption.
		#	print 'ht_capture_cc: meeting (' + self.gift_id + ') is not in OCCURRED state(' + str(CertificateState.OCCURRED) + '), in state ' + str(self.gift_state)
		#	raise StateTransitionError(self.__class__, self.gift_id, cur_state, nxt_state, self.gift_flags, user_msg='Meeting cannot perform that action')


		try:
			print 'ht_capture_cc: initialize stripe with their Key() -- get o_auth'
			o_auth = Oauth.get_stripe_by_uid(sellr_prof.account)
			print 'ht_capture_cc: initialize stripe with their Key() -- o_auth.' + o_auth.oa_secret
			stripe.api_key = o_auth.oa_secret

			print 'ht_capture_cc: go get the charge'
			stripe_charge = stripe.Charge.retrieve(self.charge_transaction)

			print 'ht_capture_cc: initialize stripe with our Key() -- ready, set, capture'
			charge = stripe_charge.capture()

			print 'ht_capture_cc: Post Charge'
			pp(charge)

			if charge['captured'] == True:
				print 'ht_capture_cc: That\'s all folks, it worked!'

			self.gift_flags = self.gift_flags | GIFT_FLAG_MONEY_CAPTURED
			self.gift_charged = dt.utcnow()  #appt_charged has no timezone, dumb, dumb, dumb
			print 'ht_capture_cc: keep the balance transaction? ' + str(charge['balance_transaction'])
		except Exception as e:
			# cannot apply application_fee when the key given is not a Stripe Connect OAuth key.
			print 'ht_capture_cc: charge[failure_code] = ' + str(charge['failure_code'])
			print 'ht_capture_cc: charge[failure_message] ' + str(charge['failure_message'])
			print 'ht_capture_cc: Exception', type(e), e
			raise e

		print 'ht_capture_cc: returning successful.'







@mngr.task
def ht_enable_reviews(gift_id):
	print 'ht_enable_reviews(' + gift_id + ')  enter'

	# ensure meeting in 'ACCEPTED' state
	meeting = Meeting.get_by_id(gift_id)
	if (not meeting or not meeting.occurred()):
		#TODO turn this into a Meeting method!
		print 'ht_enable_reviews(): ' +  meeting.gift_id + ' is not in OCCURRED state =' + meeting.gift_state
		print 'ht_enable_reviews(): continuing; we might want to stop... depends on if we lost a race; prop implemnt OCCURRED_event'
		# check to see if reviews_enabled already [If it lost a race]
		# currently spaced it out (task-timeout pops 2 hours; dashboard-timeout must occur after 4)
		return

	sellr_profile = Profile.get_by_prof_id(meeting.gift_sellr)
	buyer_profile = Profile.get_by_prof_id(meeting.gift_buyer)
	print 'ht_enable_reviews(): get account ' +  sellr_profile.account
	print 'ht_enable_reviews(): get account ' +  buyer_profile.account
	sellr_account = Account.get_by_uid(sellr_profile.account)
	buyer_account = Account.get_by_uid(buyer_profile.account)

	try:
		print 'ht_enable_reviews(): create reviews!'
		review_hp = Review(meeting.gift_id, sellr_profile.prof_id, buyer_profile.prof_id)
		review_bp = Review(meeting.gift_id, buyer_profile.prof_id, sellr_profile.prof_id)
		print 'ht_enable_reviews()  review_hp: ' + str(review_hp.review_id)
		print 'ht_enable_reviews()  review_bp: ' + str(review_bp.review_id)

		db_session.add(review_hp)
		db_session.add(review_bp)
		db_session.commit()

		print 'ht_enable_reviews()  modify meeting w/ review info'
		meeting.review_buyer = review_bp.review_id
		meeting.review_sellr = review_hp.review_id
		print 'ht_enable_reviews()  calling Meeting.writing.'
		db_session.add(meeting)
		db_session.commit()

		print 'ht_enable_reviews()  successfully created reviews, updated profile.  Disable in 30 + days.'
		review_start = meeting.gift_tf + timedelta(hours = 1)
		review_finsh = meeting.gift_tf + timedelta(days = 30)

		# Notifiy users.  Enqueue delayed review email.
		ht_send_review_reminder.apply_async(args=[sellr_account.email, sellr_profile.prof_name, meeting.gift_id, review_bp.review_id], eta=review_start)
		ht_send_review_reminder.apply_async(args=[buyer_account.email, buyer_profile.prof_name, meeting.gift_id, review_hp.review_id], eta=review_start)
		meeting_event_complete.apply_async(args=[meeting.gift_id], eta=review_finsh)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	return None



@mngr.task
def meeting_event_chargecc(gift_id):
	print 'meeting_event_chargecc(' + str(gift_id) + ')'
	try:
		# TODO: make transaction for atomicity
		meeting = Meeting.get_by_id(gift_id)
		meeting.set_state(CertificateState.CHARGECC)
		db_session.add(meeting)
		db_session.commit()
	except AttributeError as ae:
		print 'meeting_event_chargecc(' + str(gift_id) + ')\t'+ str(type(e)) + str(e)
		pass
	except Exception as e:
		print 'meeting_event_chargecc(' + str(gift_id) + ')\t'+ str(type(e)) + str(e)
		db_session.rollback()



@mngr.task
def meeting_event_occurred(gift_id):
	try:
		# TODO: make transaction for atomicity
		meeting = Meeting.get_by_id(gift_id)
		meeting.set_state(CertificateState.OCCURRED)
		db_session.add(meeting)
		db_session.commit()
	except Exception as e:
		print 'meeting_event_occured callback: ' + str(type(e)) + str(e)
		db_session.rollback()



@mngr.task
def meeting_event_complete(gift_id):
	#30 days after enable, shut it down!
	try:
		# TODO: make transaction for atomicity
		meeting = Meeting.get_by_id(gift_id)
		meeting.set_state(CertificateState.COMPLETE)
		db_session.add(meeting)
		db_session.commit()
	except Exception as e:
		print 'meeting_event_occured callback: ' + str(type(e)) + str(e)
		db_session.rollback()





#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class MeetingFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Meeting
		sqlalchemy_session = db_session

	gift_id = factory.fuzzy.FuzzyText(length=20,  chars="1234567890-", prefix='test-id-')
	gift_ts = timezone('US/Pacific').localize(dt.utcnow())
	gift_tf	= gift_ts + timedelta(hours = 4)
	gift_details	= factory.Sequence(lambda n: u'Test Description %d' % n)
	gift_location	= factory.fuzzy.FuzzyText(length=3, chars="1234567890", suffix=' Test Road, Richmond, IN 47374')
	gift_token	= factory.fuzzy.FuzzyText(length=20,  chars="1234567890-", prefix='test-token-')
	gift_card	= 'card_4VoDT440HtEKoz'
	customer	= 'cus_4VoBLFNml6SK4Q'
	gift_cost	= factory.fuzzy.FuzzyInteger(10, 100)

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		gift_ts	= kwargs.pop('gift_ts', cls.gift_ts)
		tf	= kwargs.pop('gift_tf', cls.gift_tf)
		id	= kwargs.pop('gift_id', cls.gift_id)

		review_time = gift_ts.astimezone(timezone('UTC')) + timedelta(hours=2)
		print review_time

		cost		= kwargs.pop('gift_cost',		cls.gift_cost)
		location	= kwargs.pop('gift_location',	cls.gift_location)
		details		= kwargs.pop('gift_details', 	cls.gift_details)
		token		= kwargs.pop('gift_token',		cls.gift_token)
		card		= kwargs.pop('gift_card',		cls.gift_card)
		buyer_prof	= kwargs.pop('gift_buyer',		'3239bc9b-b64e-4b93-b5ad-a92dae28223f')
		sellr_prof	= kwargs.pop('gift_sellr',		'879c3584-9331-4bba-8689-5bfb3300625a')
		#print '_create: ', ds, ' - ', df
		#print '_create: ', cost

		obj = model_class(sellr_prof, buyer_prof, gift_ts, tf, cost, location, details, token=token, card=card, *args, **kwargs)
		obj.gift_id = id #over-riding for clarity when reading the log-output
		obj.gift_flags = obj.gift_flags | GIFT_FLAG_WAIVE_FEE
		return obj
