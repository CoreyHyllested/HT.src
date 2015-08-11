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
from sqlalchemy import ForeignKey, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
import uuid, string


class Location(database.Model):
	__tablename__ = "location"
	location_id	= Column(String(40), primary_key=True, index=True)

	location_street  = Column(String(128))
	location_suite	 = Column(String(128))
	location_city	 = Column(String(64))
	location_state   = Column(String(32))
	location_zip	 = Column(String(10))

#	//developers.google.com/maps/documentation/geocoding/intro#Types
#	location_addr_room	= Column(String(64))	# PRECISE street address.
#	location_addr_floor	= Column(String(64))	# PRECISE street address.
#	location_addr_st	= Column(String(64))	# PRECISE street address.
#	location_locale		= Column(String(64))	# City, Town, Etc.  Maybe "sublocale" (Brooklyn)
#	location_aal2		= Column(String(32))	# Administrative Area  (USA => County)
#	location_aal1		= Column(String(32))	# Administrative Area  (USA => State)
#	location_aal0		= Column(String(32))	# Administrative Area  (e.g => The USA)

#	location_premise	= Named location, often a building or collection of buildings with a common name
#	location_colloquial		= Alternate name for location.
#	location_neighborhood	= Neighborhood.
#	location_intersection	= Intersecting street.
#	location_formatted	= Formatted Name(128).
#	location_postcode	= Named location, often a building or collection of buildings with a common name

	business		= Column(String(40), ForeignKey('business.bus_id'), nullable=True)
	location_lat	= Column(Float)
	location_lng	= Column(Float)
#	location_gid	= Column(String(32))	# Google Place ID.
	location_state	= Column(Integer, default = 0)

	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")


	def __init__(self, street=None, suite=None, city=None, state=None, zipcode=None, lat=None, lng=None, business_id=None):
		self.location_id	= str(uuid.uuid4())
		self.location_street = street
		self.location_suite	= suite
		self.location_city	= city
		self.location_state	= state
		self.location_zip	= zipcode

		self.location_lat	= lat
		self.location_lng	= lng

		self.business	= business_id
		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		return '<location %r>' % (self.location_id)


	def display_address(self):
		street = self.display_street_suite()
		cityst = self.display_city_state()
		if (street):
			rc = street
			if (cityst):
				rc += ', ' + cityst
		elif (cityst):
			rc = cityst
		return rc


	def display_street_suite(self):
		rc  = ''
		if self.location_street:
			rc += string.capwords(self.location_street)
			if self.location_suite:
				rc += ' ' + self.location_suite + ' '
		return rc


	def display_city_state(self):
		rc = ''
		if self.location_city:
			rc += string.capwords(self.location_city)
			if self.location_state:
				rc += ', ' + self.location_state
		elif self.location_state:
			rc += self.location_state
		return rc



	@staticmethod
	def get_by_id(id):
		location = None
		try:
			location = Location.query.filter_by(location_id=id).one()
		except NoResultFound as nrf: pass
		return location


	@staticmethod
	def from_json(json_object):
		address  = json_object['address']
		location = Location(address['street'],
							address['suite'],
							address['city'],
							address['state'],
							address['post'],
							address['meta']['lat'],
							address['meta']['lng'],
							json_object['_id']
							)
		return location


#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

