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


from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.errors		 import *
from server.models import Account, Profile, Oauth, Review
from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm	import relationship, backref
from factory.fuzzy	import *
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime as dt, timedelta, tzinfo
from pytz	import timezone
from pprint	import pprint as pp
import uuid, factory, stripe




class MeetingState:
	PROPOSED = 0		# Shows up in dashboard as proposal.
	ACCEPTED = 1		# Shows up in dashboard as appointment.
	CHARGECC = 2
	OCCURRED = 3		# Shows up in dashboard as review Opp.
	COMPLETE = 4		# Terminal state... see somewhere
	RESOLVED = 5		# Terminal state... see somewhere
	REJECTED = 10	# Terminal... see somewhere
	TIMEDOUT = 11	# Terminal... see somewhere
	CANCELED = 20	# Terminal state... see somewhere
	DISPUTED = 30

	LOOKUP_TABLE = {
		PROPOSED : 'PROPOSED',
		ACCEPTED : 'ACCEPTED',
		DISPUTED : 'DISPUTED',
		OCCURRED : 'OCCURRED',
		REJECTED : 'REJECTED',
		CANCELED : 'CANCELED',
		RESOLVED : 'RESOLVED',
		COMPLETE : 'COMPLETE',
		TIMEDOUT : 'TIMEDOUT',
		CHARGECC : 'CHARGE CREDIT CARD',	# Trans-state
	}

	@staticmethod
	def state_name(state):
		return MeetingState.LOOKUP_TABLE.get(state, 'UNDEFINED')



################################################################################
### MEETING FLAGS FIELD ########################################################
################################################################################
################################################################################
## 	NAME				## BIT		## DETAILS
################################################################################
# Occurred flags.
################################################################################
MEET_BIT_BUYER_REVIEWED =	12		# Buyer reviewed meeting
MEET_BIT_SELLR_REVIEWED =	13		# Seller reviewed meeting
MEET_BIT_MONEY_CAPTURED =	14		# Money has taken from user, 2 days after appt.
MEET_BIT_MONEY_USERPAID =	15		# Appointment Captured money and Transferred payment to Seller.
MEET_BIT_BUYER_CANCELED =	16		# Appointment was canceled by buyer.
################################################################################
### MEETING DETAILS ############################################################
################################################################################
MEET_BIT_WAIVE_FEE		=	27		# Insprite is waiving its fee.
MEET_BIT_RESPONSE		=	28		# Meeting went into negotiation.
MEET_BIT_QUIET			=	29		# Meeting was quiet
MEET_BIT_DIGITAL		=	30		# Meeting was digital
MEET_BIT_RUNOVER		=	31
################################################################################

MEET_FLAG_WAIVE_FEE		= (0x1 << MEET_BIT_WAIVE_FEE)




class Meeting(Base):
	__tablename__ = "meeting"
	meet_id		= Column(String(40), primary_key=True)													# NonSequential ID
	meet_sellr	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE SELLER. The Hero
	meet_buyer	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE BUYER; requested hero.
	meet_owner	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)						# THE PROFILE who can make a decision. (to accept, etc)
	meet_state	= Column(Integer, nullable=False, default=MeetingState.PROPOSED,	index=True)			# Pure State (as in Machine)
	meet_flags	= Column(Integer, nullable=False, default=0)											# Attributes: Quiet?, Digital?, Run-Over Enabled?
	meet_count	= Column(Integer, nullable=False, default=0)											# Number of times vollied back and forth.
	meet_cost	= Column(Integer, nullable=False, default=0)											# Cost.
	meet_ts		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	meet_tf		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	meet_tz		= Column(String(32), nullable = False)
	meet_details	= Column(String(2048), nullable = False)
	meet_location	= Column(String(1024), nullable = False)	
	meet_created = Column(DateTime(), nullable = False)
	meet_updated = Column(DateTime(), nullable = False)
	meet_secured = Column(DateTime())
	meet_charged = Column(DateTime())

	charge_customer_id	= Column(String(40), nullable = True)	# stripe customer id
	charge_credit_card	= Column(String(40), nullable = True)	# stripe credit card
	charge_transaction	= Column(String(40), nullable = True)	# stripe transaction id
	charge_user_token	= Column(String(40), nullable = True)	# stripe charge tokn
	hero_deposit_acct	= Column(String(40), nullable = True)	# hero's stripe deposit account
	review_buyer = Column(String(40), ForeignKey('review.review_id'))
	review_sellr = Column(String(40), ForeignKey('review.review_id'))


	def __init__(self, sellr_id, buyer_id, datetime_s, datetime_f, cost, location, description, token=None, customer=None, card=None, flags=None):
		self.meet_id	= str(uuid.uuid4())
		self.meet_sellr	= str(sellr_id)
		self.meet_owner	= str(sellr_id)
		self.meet_buyer	= str(buyer_id)
		self.meet_cost	= int(cost)
		self.meet_flags	= 0
		if (flags is not None): self.meet_flags = flags

		self.meet_ts	= datetime_s
		self.meet_tf	= datetime_f
		self.meet_tz	= 'US/Pacific'
		self.meet_location	= location 
		self.meet_details	= description
		self.meet_state = MeetingState.PROPOSED

		self.charge_customer_id = customer
		self.charge_credit_card = card
		self.charge_user_token = token

		#print 'Meeting(p_uid=%s, cost=%s, location=%s)' % (self.meet_id, cost, location)
		#print 'Meeting(token=%s, cust=%s, card=%s)' % (token, customer, card)

		if (token is None):		raise SanitizedException(None, user_msg = 'Meeting: stripe token is None')
		if (card is None):		raise SanitizedException(None, user_msg = 'Meeting: credit card is None')
		if (customer is None):	raise SanitizedException(None, user_msg = 'Meeting: customer is None')

		self.meet_created = dt.utcnow()
		self.meet_updated = dt.utcnow()


	def proposed(self): return (self.meet_state == MeetingState.PROPOSED)
	def accepted(self): return (self.meet_state == MeetingState.ACCEPTED)
	def occurred(self): return (self.meet_state == MeetingState.OCCURRED)
	def complete(self): return (self.meet_state == MeetingState.COMPLETE)
	def canceled(self): return (self.meet_state == MeetingState.CANCELED)


	def update(self, prof_updated, updated_s=None, updated_f=None, update_cost=None, updated_place=None, updated_desc=None, updated_state=None, updated_flags=None): 
		self.meet_owner		= prof_updated
		self.meet_count		= self.meet_count + 1
		self.meet_updated	= dt.utcnow()

		if (updated_s is not None): self.meet_ts = updated_s
		if (updated_f is not None): self.meet_tf = updated_f
		if (updated_cost is not None):	self.meet_cost	= int(updated_cost)
		if (updated_desc is not None):	self.meet_details = updated_desc
		if (updated_place is not None):	self.meet_location = updated_place
		if (updated_state is not None):	self.meet_state = updated_state
		if (updated_flags is not None):	self.meet_flags = updated_flags


	@staticmethod
	def get_by_id(meet_id):
		meeting = None
		try: meeting = Meeting.query.filter_by(meet_id=meet_id).one()
		except NoResultFound as nrf: pass
		return meeting
	

	def set_flag(self, flag):
		self.meet_flags = (self.meet_flags | flag)

	def test_flag(self, flag):
		return (self.meet_flags & flag)

	def set_state(self, nxt_state, profile=None):
		cur_state = self.meet_state
		cstate_str = MeetingState.state_name(cur_state)
		nstate_str = MeetingState.state_name(nxt_state)

		transitions = self.STATE_TRANSITION_MATRIX[cur_state]
		transition = transitions.get(nxt_state)
		if (transition is None):
			raise StateTransitionError(self.__class__, self.meet_id, cur_state, nxt_state, self.meet_flags, user_msg='Meeting cannot perform that action')

		# drive transition to next state, raising Exception if problem arises.
		successful_transition = transition(self, profile, cur_state, nxt_state)
		if (successful_transition):
			self.meet_state = nxt_state
			self.meet_updated = dt.utcnow()
		return



	def get_meet_ts(self, tz=None):
		zone = self.meet_tz or 'US/Pacific'
		return self.meet_ts.astimezone(timezone(zone))

	def get_meet_tf(self, tz=None):
		zone = self.meet_tz or 'US/Pacific'
		return self.meet_tf.astimezone(timezone(zone))

	def get_duration(self):
		return (self.meet_tf - self.meet_ts)

	def get_duration_in_hours(self):
		td = self.meet_tf - self.meet_ts
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
		description = self.meet_details.replace('\n', '<br>')
		return description
			

	def accept_url(self): return str('https://127.0.0.1:5000/meeting/accept?meet_id=' + self.meet_id)
	def reject_url(self): return str('https://127.0.0.1:5000/meeting/reject?meet_id=' + self.meet_id)
	def __repr__(self):	return '<meet %r, Hero=%r, Buy=%r, State=%r>' % (self.meet_id, self.meet_sellr, self.meet_buyer, self.meet_state)


	@property
	def serialize(self):
		return {
			'meet_id'		: self.meet_id,
			'meet_sellr'	: self.meet_sellr,
			'meet_buyer'	: self.meet_buyer,
			'meet_state'	: self.meet_state,
			'meet_flags'	: self.meet_flags,
			'meet_cost'		: self.meet_cost,
			'meet_updated'	: self.meet_updated.strftime('%A, %b %d, %Y %H:%M %p')
		}



	def __transition_proposed_to_accepted(self, profile, cur, nxt):
		if (self.meet_owner != profile.prof_id):
			print '\tOWNER - ', self.meet_owner, 'PERSON CHANGING meeting\t', profile.prof_id, profile.prof_name
			raise StateTransitionError(self.__class__, self.meet_id, cur, nxt, self.meet_flags, user_msg='Only meeting owner can perform that action')

		self.meet_secured = dt.utcnow()


		# if chargecc_time is 'in the past' (used during testing); set to five mins.
		chargecc_time = self.meet_ts.astimezone(timezone('UTC')) - timedelta(days=2)
		in_five_min = dt.now(timezone('UTC'))  + timedelta(minutes=2)
		if (in_five_min > chargecc_time): chargecc_time = in_five_min
		#print '\tMeeting.transition_PROPOSED_to_ACCEPTED(' + self.meet_id + ')\t@ ', chargecc_time.strftime('%A, %b %d, %Y %H:%M %p')

		# create event that will transition state and will charge the credit card
		meeting_event_chargecc.apply_async(args=[self.meet_id], eta=chargecc_time)
		return True



	def __transition_proposed_to_rejected(self, profile, cur, nxt):
		#print
		#print '\tMeeting.transition_PROPOSED_to_REJECTED()\tENTER\t', cur, nxt
		if (self.meet_owner != profile.prof_id):
			print '\tOWNER - ', self.meet_owner, 'PERSON CHANGING meeting\t', profile.prof_id, profile.prof_name
			raise StateTransitionError(self.__class__, self.meet_id, cur, nxt, self.meet_flags, user_msg='Only meeting owner can perform that action')

		# if (nxt == MEET_STATE_TIMEDOUT): flags = self.set_flag(MEET_BIT_TIMEDOUT)
		#print '\tMeeting.transition_PROPOSED_to_REJECTED()\tEXIT'
		return True



	def __transition_accepted_to_chargecc(self, profile, cur, nxt):
		#print '\tMeeting.transition_ACCEPTED_to_CHARGECC()\tENTER'
		self.ht_charge_creditcard()

		# if review_time is 'in the past' (used during testing); set for five mins.
		review_time = self.meet_ts.astimezone(timezone('UTC')) + timedelta(hours=2)
		in_five_min = dt.now(timezone('UTC'))  + timedelta(minutes=2)
		if (in_five_min > review_time): review_time = in_five_min

		# create transition-state event; creates both review and capture events
		meeting_event_occurred.apply_async(args=[self.meet_id], eta=review_time)
		#print '\tMeeting evt occurs @ ', review_time.strftime('%A, %b %d, %Y %H:%M %p')
		return True



	def __transition_chargecc_to_occurred(self, profile, cur, nxt):
		print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tENTER'
		capture_time = self.meet_tf + timedelta(days=2)
		capture_time = dt.now(timezone('UTC')) + timedelta(minutes=5)	#remove when done testing
		review_time	 = self.meet_tf.astimezone(timezone('UTC')) + timedelta(hours=2)
		in_five_min  = dt.now(timezone('UTC')) + timedelta(minutes=5)	#remove when done testing

		if (capture_time < in_five_min):
			print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tcapture_time too soon, set to 5 min'
			review_time = in_five_min

		if (review_time < in_five_min):
			print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tReview_time too soon, set to 5 min'
			review_time = in_five_min

		print '\tMeeting.transition_CHARGECC_to_OCCURRED()\tsend review @ ', review_time.strftime('%A, %b %d, %Y %H:%M %p')
		ht_capture_creditcard.apply_async(args=[meeting.meet_id], eta=capture_time)
		ht_enable_reviews.apply_async(args=[self.meet_id], eta=review_time)
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


	STATE_TRANSITION_MATRIX =	{	MeetingState.PROPOSED	: { MeetingState.ACCEPTED	: __transition_proposed_to_accepted,
																MeetingState.REJECTED	: __transition_proposed_to_rejected,
																MeetingState.TIMEDOUT	: __transition_proposed_to_rejected, },
									MeetingState.ACCEPTED	: { MeetingState.CHARGECC	: __transition_accepted_to_chargecc,
																MeetingState.CANCELED	: __transition_accepted_to_canceled, },
									MeetingState.CHARGECC	: { MeetingState.OCCURRED	: __transition_chargecc_to_occurred,
																MeetingState.CANCELED	: __transition_chargecc_to_canceled, },
									MeetingState.OCCURRED	: { MeetingState.COMPLETE	: __transition_occurred_to_complete,
																MeetingState.DISPUTED	: __transition_occurred_to_disputed, },
									MeetingState.COMPLETE	: { MeetingState.DISPUTED	: __transition_complete_to_disputed, },
									MeetingState.DISPUTED	: { MeetingState.DISPUTED	: __transition_disputed_to_resolved, },
								}


	def ht_charge_creditcard(self):
		print
		print 'ht_charge_creditcard: enter (' + self.meet_id + ', ' + str(self.meet_state) + ')  $' + str(self.meet_cost) + ' from cust. ' + self.charge_customer_id

		if (not self.accepted()):
			raise StateTransitionError(self.__class__, self.meet_id, self.meet_state, MEET_STATE_CHARGECC, self.meet_flags, user_msg='Currently cannot perform that action')

		try:
			sellr_profile = Profile.get_by_prof_id(self.meet_sellr)
			sellr_account = Account.get_by_uid(sellr_profile.account)
			o_auth = Oauth.get_stripe_by_uid(sellr_profile.account)
			if (o_auth is None): raise NoOauthFound(sellr_profile.account)

			print 'ht_charge_creditcard: on behalf of ' +  str(sellr_profile.prof_name) + ', ' + str(o_auth.oa_secret)

			fee = 0
			if (self.meet_cost > 5 and not self.test_flag(MEET_FLAG_WAIVE_FEE)):
				fee = int((self.meet_cost * 7.1)-30),

			print 'ht_charge_creditcard: cost (pennies)  ' +  str(self.meet_cost * 100)
			print 'ht_charge_creditcard: application fee ' +  str(fee)
			print 'ht_charge_creditcard: email_address   ' +  str(sellr_account.email)
			charge = stripe.Charge.create(
				customer=self.charge_customer_id,		# customer.id is the second one passed in
				capture=False,							# Capture later.
				amount=(self.meet_cost * 100),			# charged in pennies.
				currency='usd',
				description=self.meet_details,
				application_fee=fee,
				api_key=str(o_auth.oa_secret),
				receipt_email=str(sellr_account.email)
			)

			pp(charge)

			print 'ht_charge_creditcard: modify meeting'
			self.meet_charged = dt.now(timezone('UTC'))
			self.charge_transaction = charge['id']		 #once upon a time, this was the idea::proposal.charge_transaction = charge['balance_transaction']
			db_session.add(self)
			db_session.commit()
			print 'ht_charge_creditcard: successfully committed meeting'
		except Exception as e:
			# cannot apply application_fee if fee is negative
			# cannot apply application_fee if the given key is not a StripeConnect
			print 'ht_charge_creditcard: Exception', type(e), e
			db_session.rollback()
			dump_error(e)
			ht_sanitize_error(e)
		print 'ht_charge_creditcard: failure_code=' + str(charge['failure_code']) + ', failure_message=' + str(charge['failure_message'])






@mngr.task
def ht_capture_creditcard(meet_id):
	""" HT_capture_cc() captures money reserved. Basically, it charges the credit card. This is a big deal, don't fuck it up.
		ht_capture_cc() is delayed. That is why we must pass in meet_id, and get info from DB rather than pass in proposal.
	"""
	print 'ht_capture_cc: enter(' + meet_id + ')'
	meeting = Meeting.get_by_id(meet_id)
	(ha, hp) = get_account_and_profile(proposal.meet_sellr)	# hack, remove me...

	print 'ht_capture_cc: charge_id=' + str(proposal.charge_transaction)

	if (meeting.meet_state != MEET_STATE_OCCURRED): # and (proposal.test_flag(APPT_FLAG_MONEY_CAPTURED))):
		# update must set update_time. (if proposal.prop_updated > prev_known_update_time): corruption.
		print 'ht_capture_cc: proposal (' + meeting.meet_id + ') is not in OCCURRED state(' + str(MEET_STATE_OCCURRED) + '), in state ' + str(meeting.meet_state)
		return meeting.meet_state


	try:
		print 'ht_capture_cc: initialize stripe with their Key() -- get o_auth'
		o_auth = Oauth.get_stripe_by_uid(hp.account)
		print 'ht_capture_cc: initialize stripe with their Key() -- o_auth.' + o_auth.oa_secret
		stripe.api_key = o_auth.oa_secret

		print 'ht_capture_cc: go get the charge'
		stripe_charge = stripe.Charge.retrieve(meeting.charge_transaction)

		print 'ht_capture_cc: initialize stripe with our Key() -- ready, set, capture'
		charge = stripe_charge.capture()

		print 'ht_capture_cc: Post Charge'
		pp(charge)

		if charge['captured'] == True:
			print 'ht_capture_cc: That\'s all folks, it worked!'

		meeting.set_flag(APPT_FLAG_MONEY_CAPTURED)
		meeting.meet_charged = dt.utcnow()  #appt_charged has no timezone, dumb, dumb, dumb
		print 'ht_capture_cc: keep the balance transaction? ' + str(charge['balance_transaction'])
		print 'ht_capture_cc: adding modified meeting'
		db_session.add(meeting)
		db_session.commit()
		print 'ht_capture_cc: successfully committed meeting'

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




@mngr.task
def ht_enable_reviews(meet_id):
	print 'ht_enable_reviews(' + meet_id + ')  enter'

	# ensure meeting in 'ACCEPTED' state
	meeting = Meeting.get_by_id(meet_id)
	if (not meeting or not meeting.occurred()):
		#TODO turn this into a Meeting method!
		print 'ht_enable_reviews(): ' +  meeting.meet_id + ' is not in ACCEPTED state =' + meeting.meet_state
		print 'ht_enable_reviews(): continuing; we might want to stop... depends on if we lost a race; prop implemnt OCCURRED_event'
		# check to see if reviews_enabled already [If it lost a race]
		# currently spaced it out (task-timeout pops 2 hours; dashboard-timeout must occur after 4)
		return

	sellr_profile = Profile.get_by_prof_id(meeting.meet_sellr)
	buyer_profile = Profile.get_by_prof_id(meeting.meet_buyer)
	print 'ht_enable_reviews(): get account ' +  sellr_profile.account
	print 'ht_enable_reviews(): get account ' +  buyer_profile.account
	sellr_account = Account.get_by_uid(sellr_profile.account)
	buyer_account = Account.get_by_uid(buyer_profile.account)

	try:
		review_hp = Review(meeting.meet_id, sellr_profile.prof_id, buyer_profile.prof_id)
		review_bp = Review(meeting.meet_id, buyer_profile.prof_id, sellr_profile.prof_id)
		print 'ht_enable_reviews()  review_hp: ' + str(review_hp.review_id)
		print 'ht_enable_reviews()  review_bp: ' + str(review_bp.review_id)

		db_session.add(review_hp)
		db_session.add(review_bp)
		db_session.commit()

		print 'ht_enable_reviews()  modify Meeting.  Set state to OCCURRED.'
		meeting.review_user = review_bp.review_id
		meeting.review_hero = review_hp.review_id
		print 'ht_enable_reviews()  calling Meeting.writing.'
		db_session.add(meeting)
		db_session.commit()

		print 'ht_enable_reviews()  successfully created reviews, updated profile.  Disable in 30 + days.'
		review_start = meeting.meet_tf + timedelta(hours = 1)
		review_finsh = meeting.meet_tf + timedelta(days = 30)

		# Notifiy users.  Enqueue delayed review email.
		ht_send_review_reminder.apply_async(args=[sellr_account.email, sellr_profile.prof_name, meeting.meet_id, review_bp.review_id], eta=review_start)
		ht_send_review_reminder.apply_async(args=[buyer_account.email, buyer_profile.prof_name, meeting.meet_id, review_hp.review_id], eta=review_start)
		meeting_event_complete.apply_async(args=[meeting.meet_id], eta=review_finsh)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	return None



@mngr.task
def meeting_event_chargecc(meet_id):
	print 'meeting_event_chargecc(' + str(meet_id) + ')'
	try:
		meeting = Meeting.get_by_id(meet_id)
		meeting.set_state(MeetingState.CHARGECC)
	except AttributeError as ae:
		pass
	except Exception as e:
		print 'meeting_event_chargecc(' + str(meet_id) + ')\t'+ str(type(e)) + str(e)
		db_session.rollback()



@mngr.task
def meeting_event_occurred(meet_id):
	try:
		meeting = Meeting.get_by_id(meet_id)
		meeting.set_state(MeetingState.OCCURRED)
	except Exception as e:
		print 'meeting_event_occured callback: ' + str(type(e)) + str(e)
		db_session.rollback()



@mngr.task
def meeting_event_complete(meet_id):
	#30 days after enable, shut it down!
	try:
		meeting = Meeting.get_by_id(meet_id)
		meeting.set_state(MeetingState.COMPLETE)
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

	meet_id = factory.fuzzy.FuzzyText(length=20,  chars="1234567890-", prefix='test-id-')
	meet_ts = timezone('US/Pacific').localize(dt.utcnow())
	meet_tf	= meet_ts + timedelta(hours = 4)
	meet_details	= factory.Sequence(lambda n: u'Test Description %d' % n)
	meet_location	= factory.fuzzy.FuzzyText(length=3, chars="1234567890", suffix=' Test Road, Richmond, IN 47374')
	meet_token	= factory.fuzzy.FuzzyText(length=20,  chars="1234567890-", prefix='test-token-')
	meet_card	= 'card_4VoDT440HtEKoz'
	customer	= 'cus_4VoBLFNml6SK4Q'
	meet_cost	= factory.fuzzy.FuzzyInteger(10, 100)

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		meet_ts	= kwargs.pop('meet_ts', cls.meet_ts)
		tf	= kwargs.pop('meet_tf', cls.meet_tf)
		id	= kwargs.pop('meet_id', cls.meet_id)

		review_time = meet_ts.astimezone(timezone('UTC')) + timedelta(hours=2)
		print review_time

		cost		= kwargs.pop('meet_cost',		cls.meet_cost)
		location	= kwargs.pop('meet_location',	cls.meet_location)
		details		= kwargs.pop('meet_details', 	cls.meet_details)
		token		= kwargs.pop('meet_token',		cls.meet_token)
		card		= kwargs.pop('meet_card',		cls.meet_card)
		buyer_prof	= kwargs.pop('meet_buyer',		'3239bc9b-b64e-4b93-b5ad-a92dae28223f')
		sellr_prof	= kwargs.pop('meet_sellr',		'879c3584-9331-4bba-8689-5bfb3300625a')
		#print '_create: ', ds, ' - ', df
		#print '_create: ', cost

		obj = model_class(sellr_prof, buyer_prof, meet_ts, tf, cost, location, details, token=token, card=card, *args, **kwargs)
		obj.meet_id = id #over-riding for clarity when reading the log-output
		obj.meet_flags = obj.meet_flags | MEET_FLAG_WAIVE_FEE
		return obj
