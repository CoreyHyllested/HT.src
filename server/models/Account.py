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


from sqlalchemy 	import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm	import relationship, backref
from factory.alchemy	import SQLAlchemyModelFactory
from factory.fuzzy		import *
from werkzeug.security	import generate_password_hash, check_password_hash
from datetime import datetime as dt, timedelta
import datetime, uuid, factory

from server import database
from server.infrastructure.errors	import *
from server.models.shared	import *



class Account(database.Model):
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
	source  = Column(Integer,		nullable=False, default=OauthProvider.NONE)
	phone	= Column(String(20))
	created = Column(DateTime())
	updated = Column(DateTime())
	sec_question = Column(String(128))
	sec_answer   = Column(String(128))
	stripe_cust	 = Column(String(64))
	role		 = Column(Integer, nullable=False, default=AccountRole.CUSTOMER)
	email_policy = Column(Integer, default = 0)

	# all user profiles
	profiles = relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

	def __init__ (self, user_name, email, passhash, phone=None, ref=None, role=None):
		self.userid = str(uuid.uuid4())
		self.name   = user_name
		self.email  = email
		self.phone	= phone
		self.pwhash	= passhash
		self.role	 = role
		self.created = dt.utcnow()
		self.updated = dt.utcnow()
		self.sec_question = str(uuid.uuid4())


	def __repr__ (self): return '<Account %r, %r, %r>'% (self.userid, self.name, self.email)
	def __str__  (self): return '<Account %r, %r, %r>'% (self.userid, self.name, self.email)





	def reset_security_question(self):
		try:
			self.sec_question = str(uuid.uuid4())
			self.updated = dt.utcnow()
			database.session.add(self)
			database.session.commit()
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return None
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




	@staticmethod
	def get_by_uid(uid):
		account = None
		try:
			account = Account.query.filter_by(userid=uid).one()
		except NoResultFound as nrf: pass
		return account



	@staticmethod
	def get_by_email(email_address):
		account = None
		try:
			account = Account.query.filter_by(email=email_address.lower()).one()
		except NoResultFound as nrf: pass
		return account



	@staticmethod
	def create_account(name, email, passwd, phone=None, addr=None, ref_id=None, role=AccountRole.CUSTOMER):
		account = Account.get_by_email(email)
		if (account): raise AccountError(email, 'Email address already exists. Sign in?')
		return Account(name, email, generate_password_hash(passwd), phone=phone, ref=ref_id, role=role)



	@staticmethod
	def authorize_with_password(email, password):
		account = Account.get_by_email(email)
		if (account and check_password_hash(account.pwhash, str(password))):
			return account
		return None



	@staticmethod
	def authorize_with_hashcode(email, hashcode):
		account = Account.get_by_email(email)
		try:
			if account and account.sec_question != hashcode:
				raise NoResultFound('what is passed in -- who knows!')

			# success, save
			account.set_sec_question("")
			account.set_status(Account.USER_ACTIVE)
			database.session.add(account)
			database.session.commit()
		except NoResultFound as nrf:
			pass
		except Exception as e:
			database.session.rollback()
			account = None
		return account




#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class AccountFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Account
		sqlalchemy_session = database.session

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
