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


from server import sc_server, database
from server.infrastructure.errors	import *
from server.models.Location			import *
from server.models.shared			import *
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm  import relationship, backref

import os, re, uuid, json
from pytz import timezone
from datetime import datetime as dt, timedelta
from pprint import pprint as pp



class Business(database.Model):
	__tablename__ = "business"
	bus_id		= Column(String(40), primary_key=True, index=True)
	bus_name	= Column(String(99), nullable=False)
	bus_state	= Column(Integer,	 nullable=False, default = 0)

	# contact information.
	bus_website	= Column(String(128))
	bus_phone	= Column(String(20))
	bus_email	= Column(String(64))

	bus_account		= Column(String(40), ForeignKey('account.userid'))
	bus_headline	= Column(String(140))
	bus_description	= Column(String(5000))
	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")


	def __init__(self, name, phone=None, email=None, website=None, sources=0, id=None):
		if not id: id = str(uuid.uuid4())
		print 'Business: creating (%s|%s)' % (str(name), id)

		self.bus_id		 = id
		self.bus_name	 = name
		self.bus_state	 = sources
		self.bus_website = website

		self.bus_phone 	 = phone
		self.bus_email	 = email

		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		return '<business %r>' % (self.bus_id)

	@property
	def serialize(self):
		return {
			'business_id'	: self.bus_id,
			'business_name'	: self.bus_name,
		}

	@property
	def serialize_id(self):
		return {
			'business_id'	: self.bus_id,
			'business_name'	: self.bus_name,
			'business_website'	: self.bus_website,
			'business_emails'	: [ self.bus_email ],
			'business_phones'	: [ self.bus_phone ],
			'address'	: {}
		}


	@staticmethod
	def get_by_id(id, check_json=False):
		business = None
		try:
			# cannot throw MultipleResultsFound, DB uniqueness
			business = Business.query.filter_by(bus_id=id).one()
		except NoResultFound as nrf:
			if check_json and Business.get_json_index().get(id):
				# return Business object, save Location.
				business = Business.import_from_json(id)
		return business



	@staticmethod
	def search(identifier):
		comp_bus = []
		query = '%' + identifier.strip().lower() + '%'

		try:
			location = aliased(Location, name='location')
			comp_bus = database.session.query(Business, location)	\
						.filter(Business.bus_name.ilike(query))		\
						.outerjoin(location, Business.bus_id == location.business)	\
						.limit(5).all()
			for cb in comp_bus:
				display_composite_business(cb)
		except NoResultFound as nrf:
			pass
		return comp_bus



	@staticmethod
	def from_json(json_object, fromuser=False):
		sources = json_object.get('sources')
		website	= json_object.get('business_website')
		phones	= json_object.get('business_phones')
		emails	= json_object.get('business_emails')
		if (fromuser): sources.append({name : 'user_add'})

		contact_phone = phones[0] if phones else None
		contact_email = emails[0] if emails else None
		sources_flags = 0
		for source in sources:
			print '%s %08x' % (source['name'], BusinessSource.get_mask(source['name']))
			sources_flags = BusinessSource.set(sources_flags, BusinessSource.get_mask(source['name']))

		business = Business(json_object['business_name'],
							phone=contact_phone,
							email=contact_email,
							website=website,
							sources=sources_flags,
							id=json_object['_id'])
		try:
			print 'committing (%s|%s)' % (business.bus_name, business.bus_id)
			database.session.add(business)
			database.session.commit()
			print 'committed.'
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return None
		return business



	@staticmethod
	def import_from_json(bus_id):
		json_object = Business.get_json_index().get(bus_id)
		business = Business.from_json(json_object)
		location = Location.from_json(json_object)

		try:
			print location.location_id, business.bus_id
			database.session.add(location)
			database.session.commit()
			print 'committed business, location'
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return None
		return business



	@staticmethod
	def get_json_index():
		if sc_server.trusted_index:
			return sc_server.trusted_index

		print 'Priming Search.'
		trusted_idx = {}

		try:
			fp = open(os.getcwd() + '/server/static/root/companies.json')
			trusted_list = json.loads(fp.read())
			for account in trusted_list:
				if account.get('_status'):
					print account['_status']
					continue
				if account.get('_ignore') or not account.get('_id'):
					#print 'Missing-id', account['business_name']
					continue
				trusted_idx[account['_id']] = account
		except Exception as e:
			print type(e), e
		finally:
			if (fp): fp.close()
			sc_server.trusted_index = trusted_idx
			print 'Professional index: %d entries' % len(trusted_idx)

		return trusted_idx





#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################

def display_composite_business(composite):
	# COMPOSITE OBJECT
	# OBJ.Business	# Business
	# OBJ.location	# location of Business (maybe None)

	composite.display_city = 'No address listed'
	composite.display_addr = 'No address listed'

	if composite.location:
		composite.display_city = composite.location.display_city_state()
		composite.display_addr = composite.location.display_address()



#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

