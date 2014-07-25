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
from datetime import datetime as dt, timedelta



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
	def __init__ (self, account, service, userid, token=None, secret=None, email=None, data1=None, data2=None, data3=None):
		self.ht_account = account
		self.oa_account = userid
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



