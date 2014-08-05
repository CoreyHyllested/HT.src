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
from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime
import uuid



class Email(Base):
	__tablename__ = "email"

	id = Column(Integer, primary_key = True)
	ht_account	= Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
	email	= Column(String(128),	nullable=False, unique=True, index=True)
	flags	= Column(Integer,		nullable=True)
	created	= Column(DateTime(),	nullable=True)
	

	def __init__ (self, account, email, flags=None):
		self.ht_account = account
		self.email = email
		self.flags = flags
		self.created = dt.utcnow()
	

	def __repr__(self):
		print '<%r>' % (self.email)


	@staticmethod
	def get_account_id(email):
		account_id = None
		try:
			user_email = Oauth.query.filter_by(email=email).one()
			account_id = user_email.ht_account
		except NoResultFound as none:
			print 'Error: found zero email accounts for ', email
		return account_id




