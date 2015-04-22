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
from server.infrastructure.errors	import *
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm	import relationship, backref
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy	 import *
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime, uuid, factory


OAUTH_NONE   = 0
OAUTH_LINKED = 1
OAUTH_STRIPE = 2
OAUTH_GOOGLE = 3
OAUTH_FACEBK = 4
OAUTH_TWITTR = 5

################################################################################
### EMAIL POLICY FIELD #########################################################
################################################################################
################################################################################
## 	BIT-RANGE		NAME			DETAILS
################################################################################
## 	0 - 4			Receipts			Receipts for action taken.
##	8 				USERMSG_RECVD		Notification that user sent a message.
##  9				REVIEW_POSTED		Notificaiton that a user reviewed you.
##  16				Meeting Reminder	Reminder sent 24 hours before.
################################################################################
##  4-15,18,19,21-31				reserved
################################################################################

class EmailPolicy:
	# Receipts for actions I take
	EMAIL_BIT_RECPT_ACCEPT = 0
	EMAIL_BIT_RECPT_REJECT = 1
	EMAIL_BIT_RECPT_CANCEL = 2
	EMAIL_BIT_RECPT_REVIEW = 3
	EMAIL_BIT_RECPT_MESSGE = 4

	# Non-Critical Messages to a user.
	EMAIL_BIT_USERMSG_RECVD = 8
	EMAIL_BIT_REVIEW_POSTED = 9

	# Reminder emails.
	EMAIL_BIT_REMIND_MEETING = 16
	EMAIL_BIT_REMIND_REVIEWS = 17

	# Receipts for actions I take
	EMAIL_POLICY_RECPT_ACCEPT = (0x1 << EMAIL_BIT_RECPT_ACCEPT)
	EMAIL_POLICY_RECPT_REJECT = (0x1 << EMAIL_BIT_RECPT_REJECT)
	EMAIL_POLICY_RECPT_CANCEL = (0x1 << EMAIL_BIT_RECPT_CANCEL)
	EMAIL_POLICY_RECPT_REVIEW = (0x1 << EMAIL_BIT_RECPT_REVIEW)
	EMAIL_POLICY_RECPT_MESSGE = (0x1 << EMAIL_BIT_RECPT_MESSGE)
	EMAIL_POLICY_RECEIPTS = EMAIL_POLICY_RECPT_ACCEPT | EMAIL_POLICY_RECPT_REJECT | EMAIL_POLICY_RECPT_CANCEL | EMAIL_POLICY_RECPT_REVIEW | EMAIL_POLICY_RECPT_MESSGE

	# Non-Critical Messages to a user.
	EMAIL_POLICY_USERMSG_RECVD	= (0x1 << EMAIL_BIT_USERMSG_RECVD)
	EMAIL_POLICY_REVIEW_POSTED	= (0x1 << EMAIL_BIT_REVIEW_POSTED)
	EMAIL_POLICY_REMIND_MEETING = (0x1 << EMAIL_BIT_REMIND_MEETING)
	EMAIL_POLICY_REMIND_REVIEWS = (0x1 << EMAIL_BIT_REMIND_REVIEWS)



class AccountRole:
	CUSTOMER		= 0
	CRAFTSPERSON	= 16
	ADMIN			= 1024

	LOOKUP_TABLE = {
		CUSTOMER		: 'CUSTOMER',
		CRAFTSPERSON	: 'CRAFTSPERSON',
		ADMIN			: 'ADMIN',
	}

	@staticmethod
	def name(state):
		return AccountRole.LOOKUP_TABLE.get(state, 'UNDEFINED')




class Account(Base):
	"""Account maintains identity information each individual."""
	__tablename__ = "account"

	USER_UNVERIFIED = 0
	USER_ACTIVE		= 1
	USER_INACTIVE	= -1
	USER_BANNED		= -2

	userid  = Column(String(40), primary_key=True, index=True, unique=True)
	email   = Column(String(128), nullable=False,  index=True, unique=True)
	name    = Column(String(128), nullable=False)
	pwhash	= Column(String(128), nullable=False)
	status  = Column(Integer,		nullable=False, default=USER_UNVERIFIED)   
	source  = Column(Integer,		nullable=False, default=OAUTH_NONE)
	phone	= Column(String(20))
	created = Column(DateTime())
	updated = Column(DateTime())
	sec_question = Column(String(128))
	sec_answer   = Column(String(128))
	stripe_cust	 = Column(String(64))
	role		 = Column(Integer, nullable=False, default=AccountRole.CUSTOMER)
	email_policy = Column(Integer, default = 0)
	referred_by	= Column(String(40), ForeignKey('referral.ref_id'))

	# all user profiles
	profiles = relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

	def __init__ (self, user_name, user_email, user_pass, user_phone=None, ref=None, role=None):
		self.userid = str(uuid.uuid4())
		self.name   = user_name
		self.email  = user_email
		self.phone	= user_phone
		self.pwhash	= user_pass
		self.role	 = role
		self.created = dt.utcnow()
		self.updated = dt.utcnow()
		self.sec_question = str(uuid.uuid4())
		self.referred_by = ref


	def __repr___ (self):
		return '<Account %r, %r, %r>'% (self.userid, self.name, self.email)


	@staticmethod
	def get_by_uid(uid):
		account = None
		try:
			account = Account.query.filter_by(userid=uid).one()
		except NoResultFound as none:
			pass
		return account


	@staticmethod
	def get_by_email(email_address):
		account = None
		try:
			account = Account.query.filter_by(email=email_address.lower()).one()
		except NoResultFound as none:
			pass
		return account


	def reset_security_question(self):
		self.sec_question = str(uuid.uuid4())
		self.updated = dt.utcnow()
		return self.sec_question

	def set_email(self, e):
		self.email = e
		self.updated = dt.utcnow()
		return self
	
	def set_name(self, n):
		self.name = n
		self.updated = dt.utcnow()
		return self
	
	def set_source(self, src):
		self.source = src
		self.updated = dt.utcnow()
		return self
	
	def set_status(self, s):
		self.status = s
		self.updated = dt.utcnow()
		return self
		
	def set_sec_question(self, q):
		self.sec_question = q
		self.updated = dt.utcnow()
		return self

	def set_sec_answer(self, a):
		self.sec_answer = a
		self.updated = dt.utcnow()
		return self

	def update(self, acct_dictionary):
		self.__dict__.update(acct_dictionary)




#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class AccountFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Account
		sqlalchemy_session = db_session

	name	= factory.Sequence(lambda n: u'Test User %d' % n)
	email	= factory.Sequence(lambda n: u'corey+TestUser%d@insprite.co' % n)
	userid	= factory.fuzzy.FuzzyText(length=30, chars="1234567890-", prefix='test-uid-')

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		uid = kwargs.pop('userid',	cls.userid)
		n	= kwargs.pop('name',	cls.name)
		e	= kwargs.pop('email',	cls.email)
		pw	= kwargs.pop('pwhash', 'No password')
		#print '_create: name = ', n

		obj = model_class(n, e, pw, *args, **kwargs)
		obj.pwhash = 'pwtest'
		obj.userid = uid
		return obj
