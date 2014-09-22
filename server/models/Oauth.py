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
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy	import *
from datetime import datetime as dt, timedelta
import factory


OAUTH_NONE   = 0
OAUTH_LINKED = 1
OAUTH_STRIPE = 2
OAUTH_GOOGLE = 3
OAUTH_FACEBK = 4
OAUTH_TWITTR = 5


class Oauth(Base):
	__tablename__ = "oauth"
	id      = Column(Integer, primary_key = True)
	ht_account	= Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)		#HT UserID
	oa_account	= Column(String(64), nullable=False, index=True)		#user id returned back		#OA UserID
	oa_service	= Column(Integer(),  nullable=False)	#LINKEDIN = 1, Google = 2					#OA Service
	oa_flags	= Column(Integer(),  nullable=False)	# (valid?									#OA Flags
	oa_email	= Column(String(128))									#OA Email
	oa_token	= Column(String(256))
	oa_secret	= Column(String(64))													#OA SECRET -- for remote call
	oa_optdata1 = Column(String(256))
	oa_optdata2 = Column(String(256))
	oa_optdata3 = Column(String(256))
	oa_created	= Column(DateTime()) 	#first login time.											#OA first
	oa_ts_login	= Column(DateTime()) 	#last  login time.


	#Oauth(uid, OAUTH_STRIPE, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
	def __init__ (self, ht_userid, service, oa_userid, token=None, secret=None, email=None, data1=None, data2=None, data3=None):
		self.ht_account = ht_userid
		self.oa_account = oa_userid
		self.oa_service = service
		self.oa_flags	= 0
		self.oa_created	= dt.utcnow()
		self.oa_ts_login = dt.utcnow()

		self.oa_token	= token
		self.oa_secret	= secret
		self.oa_email	= email


	def __repr__ (self):
		return '<oauth, %r %r %r>' % (self.ht_account, self.oa_service, self.oa_account)

	@staticmethod
	def get_stripe_by_uid(uid):
		try:
			stripe_user = Oauth.query.filter_by(ht_account=uid).filter_by(oa_service=str(OAUTH_STRIPE)).one()
		except MultipleResultsFound as multiple:
			print 'Never Happen Error: found multiple Stripe customers for UID', uid
			stripe_user = None
		except NoResultFound as none:
			stripe_user = None
		return stripe_user


	@property
	def serialize(self):
		return {
			'ht_account'	: self.ht_account,
			'oa_account'	: self.oa_account,
			'oa_service'	: self.oa_service,
			'oa_flags'	: self.oa_flags,
			'oa_email'	: self.oa_email,
			'oa_token'	: self.oa_token,
			'oa_secret'	: self.oa_secret,
			'oa_optdata1'	: self.oa_optdata1,
			'oa_optdata2'	: self.oa_optdata2,
			'oa_optdata3'	: self.oa_optdata3,
		}



#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class OauthFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Oauth
		sqlalchemy_session = db_session

	oa_account	= factory.fuzzy.FuzzyText(length=30, chars="1234567890-", prefix='oauth-oa_account-')
	ht_account	= factory.fuzzy.FuzzyText(length=30, chars="1234567890-", prefix='oauth-ht_account-')

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		oa_account = kwargs.pop('oa_account', cls.oa_account)
		ht_account = kwargs.pop('ht_account', cls.ht_account)
		service = kwargs.pop('service',	OAUTH_STRIPE)
		#token	= 'pk_test_d3gRvdhkXhLBS3ABhRPhOort'
		#secret	= 'sk_test_wNvqK0VIg7EqgmeXxiOC62md'

		#token	= 'pk_test_dsbhSXD9aQLueKZ8JSeNbciU'	#Frank U
		#secret  = 'sk_test_knGq2VEMJonKFlNh1wo2Srye'	#Frank U

		token	= 'pk_test_Wo4o8A6htBjZ0gOpamMKaXFh'	# Corey
		secret	= 'sk_test_VHAFCveolOCrJX050GJ9HhfQ'	# corey #insprite

		obj = model_class(ht_account, service, oa_account, token=token, secret=secret, *args, **kwargs)
		return obj
