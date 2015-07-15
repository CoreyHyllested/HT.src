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


from server import database
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm  import relationship, backref

import uuid
from pytz import timezone
from datetime import datetime as dt, timedelta



class Business(database.Model):
	__tablename__ = "business"
	bus_id		= Column(String(40), primary_key=True, index=True)
	bus_address	= Column(String(40), ForeignKey('location.location_id'), nullable=False)
	bus_name	= Column(String(99), 									 nullable=False)
	bus_state	= Column(Integer, nullable=False, default = 0)

	# contact information.
	bus_website	= Column(String(128))
	bus_phone	= Column(String(20))
	bus_email	= Column(String(64))

	bus_account		= Column(String(40), ForeignKey('account.userid'))
	bus_headline	= Column(String(140))
	bus_description	= Column(String(5000))
	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")


	def __init__(self, name, location_id, phone=None, email=None, website=None, id=str(uuid.uuid4())):
		print 'Business: init \'' + '\''
		self.bus_id		 = id
		self.bus_name	 = name
		self.bus_address = location_id
		self.bus_website = website
		self.bus_phone 	 = phone
		self.bus_email	 = email

		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		return '<business %r>' % (self.bus_id)


	@staticmethod
	def get_by_id(id):
		business = None
		try:
			# cannot throw MultipleResultsFound, DB uniqueness
			business = Business.query.filter_by(bus_id=id).one()
		except NoResultFound as nrf: pass
		return business



	@staticmethod
	def import_from_json(import_id, json_object):
		print 'Profile: import \'' + str(import_id) + '\''
		pass



#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################
