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


from __future__ import absolute_import
from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import uuid



class BusinessReference(Base):
	__tablename__ = "businessreference"
	br_uuid     = Column(String(40), primary_key = True, index=True, unique=True)
	br_bus_acct = Column(String(40), ForeignKey('account.userid'),  nullable=False)
	br_bus_prof = Column(String(40), ForeignKey('profile.prof_id'), nullable=False)
	br_req_mail = Column(String(64), nullable=False)    #
	br_req_prof = Column(String(40), nullable=True)     # update if/when we have a profile
	br_flags    = Column(Integer)
	created     = Column(DateTime())
	updated     = Column(DateTime())
	
	def __init__ (self, acct_id, prof_id, email):
		self.br_uuid = str(uuid.uuid4())
		self.br_bus_acct = acct_id
		self.br_bus_prof = prof_id
		self.br_req_mail = email
		self.created = dt.utcnow()
		self.updated = dt.utcnow()

	def __repr__(self):
		print '<BusRefReq %r for pid:%r>' % (self.br_req_mail, self.br_bus_prof)

	@staticmethod
	def get_by_id(uuid):
		brr = None
		try:
			brr = BusinessReference.query.filter_by(br_uuid=uuid).one()
		except NoResultFound as nrf:
			pass
		return brr


	@staticmethod
	def get_by_email(bus_prof, email):
		brr = None
		try:
			brr = BusinessReference.query.filter_by(br_req_mail=email, br_bus_prof=bus_prof).one()
		except NoResultFound as nrf:
			pass
		return brr
