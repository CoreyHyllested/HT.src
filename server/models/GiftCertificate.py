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





class GiftCertificate(Base):
	__tablename__ = "giftcertificate"
	gift_id		= Column(String(40), primary_key=True)													# NonSequential ID
	gift_state	= Column(Integer, nullable=False, default=CertificateState.CREATED)
	gift_value	= Column(Integer, nullable=False, default=0)
	gift_flags	= Column(Integer, nullable=False, default=0)											# Attributes: Quiet?, Digital?, Run-Over Enabled?

	gift_recipient_name = Column(String(64))	# may only have email
	gift_recipient_mail = Column(String(64), nullable = False)
	gift_recipient_cell = Column(String(16))
	gift_recipient_addr = Column(String(128))
	gift_recipient_note = Column(String(256))
	gift_recipient_proj = Column(String(40), ForeignKey('project.proj_id'))
	gift_recipient_prof = Column(String(40), ForeignKey('profile.prof_id'))

	gift_purchaser_name = Column(String(64), nullable=False)
	gift_purchaser_mail = Column(String(64), nullable=False)
	gift_purchaser_cost = Column(Integer, nullable=False, default=0)
	gift_purchaser_prof = Column(String(40), ForeignKey('profile.prof_id'))

	gift_stripe_transaction = Column(String(40)) #charge_transaction	= Column(String(40), nullable = True)	# stripe transaction id
	gift_stripe_chargetoken = Column(String(40)) # charge_user_token	= Column(String(40), nullable = True)	# stripe charge tokn
	gift_stripe_creditcard = Column(String(40)) #charge_credit_card	= Column(String(40), nullable = True)	# stripe credit card
	gift_stripe_customerid = Column(String(40)) #charge_customer_id	= Column(String(40), nullable = True)	# tethers to OUR customer id
#	gift_stripe_amountpaid = Column(Integer, default=0)

	gift_dt_created = Column(DateTime(), nullable = False)
	gift_dt_updated = Column(DateTime(), nullable = False)
	gift_dt_charged = Column(DateTime())




	def __init__(self, recipient, purchaser, stripe):
		print 'GiftCertificate - create'
		self.gift_id	= str(uuid.uuid4())
		self.gift_state = CertificateState.CREATED
		self.gift_value = stripe.get('gift_value', 50000)
		self.gift_flags	= 0

		self.gift_recipient_mail = recipient['mail']			#required
		self.gift_recipient_name = recipient.get('name', None)
		self.gift_recipient_cell = recipient.get('cell', None)
		self.gift_recipient_addr = recipient.get('addr', None)
		self.gift_recipient_note = recipient.get('note', None)
		self.gift_recipient_prof = recipient.get('prof', None)

		self.gift_purchaser_prof = purchaser.get('prof', None)
		self.gift_purchaser_name = purchaser.get('name', None)	# required
		self.gift_purchaser_mail = purchaser.get('mail', None)	# required
		self.gift_purchaser_cost = int(purchaser.get('cost', 500)) * 100		#required, how much user required to pay, may be different from gift_value.  [in pennies]
		print 'GiftCertificate - recipient: ', self.gift_recipient_name, self.gift_recipient_mail
		print 'GiftCertificate - purchaser: ', self.gift_purchaser_name, self.gift_purchaser_mail, self.gift_purchaser_cost, self.gift_purchaser_prof

		self.gift_stripe_customerid = stripe.get('customerid', None)
		self.gift_stripe_creditcard = stripe.get('creditcard', None)
		self.gift_stripe_transaction = stripe.get('transaction', None)
		self.gift_stripe_chargetoken = stripe.get('token', None)

		self.gift_dt_created = dt.utcnow()						# required
		self.gift_dt_updated = dt.utcnow()						# required
		#if (token is None):		raise SanitizedException(None, user_msg = 'Meeting: stripe token is None')
		#if (card is None):		raise SanitizedException(None, user_msg = 'Meeting: credit card is None')
		#if (customer is None):	raise SanitizedException(None, user_msg = 'Meeting: customer is None')

		#print 'GiftCertificate(p_uid=%s, cost=%s, location=%s)' % (self.gift_id, cost, location)


	def created(self): return (self.gift_state == CertificateState.CREATED)
	def paidfor(self): return (self.gift_state == CertificateState.PAIDFOR)
	def claimed(self): return (self.gift_state == CertificateState.CLAIMED)
	def applied(self): return (self.gift_state == CertificateState.APPLIED)
	def done(self): return (self.gift_state == CertificateState.DONE)



	def update(self, updated_desc=None):
		self.gift_updated	= dt.utcnow()
		if (updated_desc is not None):	self.gift_details = updated_desc



	@staticmethod
	def get_by_giftid(gift_id):
		gift = None
		try: gift = GiftCertificate.query.filter_by(gift_id=gift_id).one()
		except NoResultFound as nrf: pass
		return gift
	
	@staticmethod
	def get_user_credit_amount(profile):
		credit = 0
		#print 'GiftCertificate.get_usercredit' ,  profile.prof_id, 'credit', credit
		try:
			gifts = db_session.query(GiftCertificate).filter(GiftCertificate.gift_recipient_prof == profile.prof_id).all()
		except Exception as e:
			print e

		for certificate in gifts:
			#print 'get_usercredit ', str(credit)
			credit = credit + certificate.gift_value
		return (credit/100)


	def get_value():
		return (certificate.gift_value / 100)


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
			raise StateTransitionError(self.__class__, self.gift_id, cur_state, nxt_state, self.gift_flags, user_msg='GiftCertificate cannot perform that action')

		# attempt transition to next state, raising Exception if problem arises.
		print 'GiftCertificate.set_state(' + nstate_str + ')'
		successful_transition = transition_process(self, profile, cur_state, nxt_state)
		if (successful_transition):
			self.gift_state = nxt_state
			self.gift_updated = dt.utcnow()
		return



	def __repr__(self):	return '<Gift %r, State=%r>' % (self.gift_id, self.gift_state)


	@property
	def serialize(self):
		return {
			'gift_id'				: self.gift_id,
			'gift_purchaser_cost'	: self.gift_purchaser_cost,
			'gift_updated'			: self.gift_updated.strftime('%A, %b %d, %Y %H:%M %p')
		}



	def capture(self):
		print 'GiftCertificate.capture: ' + self.gift_id + ', ' + str(self.gift_state)  + ',', self.gift_purchaser_cost
		fee = int((self.gift_purchaser_cost * 7.1)-30)

		print 'GiftCertificate.capture: create token'
		print 'GiftCertificate.capture: cost (pennies)  ' +  str(self.gift_purchaser_cost)
		print 'GiftCertificate.capture: application fee ' +  str(fee)
		print 'GiftCertificate.capture: email_address   ' +  str(self.gift_purchaser_mail)

		token  = None
		charge = None
		try:

			print 'GiftCertificate.capture: create charge use ', self.gift_stripe_chargetoken
			charge = stripe.Charge.create(
				amount=(self.gift_purchaser_cost),			# charged in pennies.
				currency='usd',
				capture=True,
				description='$500 gift certificate',
				#application_fee=fee,
				source=self.gift_stripe_chargetoken,
				#api_key=str(o_auth.oa_secret),
				api_key = "sk_test_wNvqK0VIg7EqgmeXxiOC62md",
				receipt_email= str(self.gift_purchaser_mail)
#				statement_description='Insprite.co',
			)
			print 'GiftCertificate.capture: modify gift'
			db_session.add(self)
			self.gift_stripe_transaction = charge['id']
			self.gift_charged = dt.now(timezone('UTC'))
			db_session.commit()
			print 'GiftCertificate.capture: successfully committed gift'
		except Exception as e:
			# cannot apply application_fee if fee is negative
			# cannot apply application_fee if the given key is not a StripeConnect
			print 'GiftCertificate.capture: Exception', type(e), e
			print 'GiftCertificate.capture: charge.failure_code =' + str(charge.get('failure_code')) + ', failure_message=' + str(charge.get('failure_message'))
			dump_error(e)
			ht_sanitize_error(e)
		finally:
			if (token  is not None): pp(token)
			if (charge is not None): pp(charge)
		print 'sc_charge_cc: exit'




	STATE_TRANSITION_MATRIX =	{	
									CertificateState.CREATED : { CertificateState.CREATED: None, },
									CertificateState.PAIDFOR : { CertificateState.CREATED: None, },
								}




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
def meeting_event_chargecc(gift_id):
	try:
		meeting = Meeting.get_by_id(gift_id)
		meeting.set_state(CertificateState.PAIDFOR)
		db_session.add(meeting)
		db_session.commit()
	except AttributeError as ae:
		pass
	except Exception as e:
		db_session.rollback()






#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class GiftCertificateFactory(SQLAlchemyModelFactory):
	class Meta:
		model = GiftCertificate
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
