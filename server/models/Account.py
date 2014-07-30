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
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy import LargeBinary
from sqlalchemy.orm	import relationship, backref
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime, uuid, factory


OAUTH_NONE   = 0
OAUTH_LINKED = 1
OAUTH_STRIPE = 2
OAUTH_GOOGLE = 3
OAUTH_FACEBK = 4
OAUTH_TWITTR = 5


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
	dob     = Column(DateTime())
	created = Column(DateTime())
	updated = Column(DateTime())
	sec_question = Column(String(128))
	sec_answer   = Column(String(128))
	stripe_cust	 = Column(String(64))
	role		 = Column(Integer, default = 0)

	# all user profiles
	profiles = relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

	def __init__ (self, user_name, user_email, user_pass):
		self.userid = str(uuid.uuid4())
		self.name   = user_name
		self.email  = user_email
		self.pwhash	= user_pass
		self.created = dt.utcnow()
		self.updated = dt.utcnow()

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
			account = Account.query.filter_by(email=email_address).one()
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
	
	def set_dob(self, bd):
		self.dob = bd
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

	def update(self, new_values_dict):
		self.__dict__.update(new_values_dict)




#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class AccountFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Account
		sqlalchemy_session = db_session

	name = factory.Sequence(lambda n: u'Test User %d' % n)
	email = factory.Sequence(lambda n: u'corey+TestUser%d@insprite.co' % n)

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		n	= kwargs.pop('name', cls.name)
		e	= kwargs.pop('email', cls.email)
		pw	= kwargs.pop('pwhash', 'No password')
		print '_create: name = ', n

		obj = model_class(n, e, pw, *args, **kwargs)
		obj.pwhash = 'pwtest'
		return obj
