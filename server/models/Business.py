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


	def __init__(self, name, phone=None, email=None, website=None, id=None):
		print 'Business: creating (%s)' % (str(name))
		self.bus_id		 = id
		self.bus_name	 = name
		self.bus_website = website

		self.bus_phone 	 = phone
		self.bus_email	 = email
		if not self.bus_id: self.bus_id = str(uuid.uuid4())

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
			print 'get_by_id(%s) ' % id
			# cannot throw MultipleResultsFound, DB uniqueness
			business = Business.query.filter_by(bus_id=id).one()
			print business
		except NoResultFound as nrf:
			if check_json:
				bus_json = Business.get_json_index().get(bus_id)

				if bus_json:
					# converting json to a Business object.
					business = Business.from_json(bus_json)
					business.from_json = True
		return business



	@staticmethod
	def search(identifier, check_json=False):
		businesses = []

		try:
			query = '%' + identifier.lower().strip() + '%'
			businesses = Business.query.filter(Business.bus_name.ilike(query)).limit(5).all()
			for x in businesses:
				print x.bus_id, x.bus_name
		except NoResultFound as nrf:
			pass
		return businesses



	@staticmethod
	def from_json(json_object):
		website	= json_object.get('business_website')
		phones	= json_object.get('business_phones')
		emails	= json_object.get('business_emails')

		contact_phone = phones[0] if phones else None
		contact_email = emails[0] if emails else None

		business = Business(json_object['business_name'],
							phone=contact_phone,
							email=contact_email,
							website=website,
							id=json_object['_id'])
		return business


	@staticmethod
	def import_from_json(bus_id):
		json_object = Business.get_json_index().get(bus_id)
		business = Business.from_json(json_object)
		location = Business.from_json(json_object)

		try:
			print location.location_id, business.bus_id
			database.session.add(location)
			database.session.commit()
			database.session.add(business)
			database.session.commit()
			print 'committed business, location'
			pp(business)
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return None
		return business


	@staticmethod
	def get_json_index():
		if (sc_server.__dict__.get('pro_index_id')):
			# return the professional business index.
			return sc_server.__dict__['pro_index_id']

		try:
			print 'Priming Search.'
			fp = open(os.getcwd() + '/server/static/root/companies.json')
			sc_server.pro_list = json.loads(fp.read())
			sc_server.pro_index_id = {}
			for account in sc_server.pro_list:
				if account.get('_status'):
					print account['_status']
					continue
				if account.get('_ignore'):
					continue
				if account.get('_ignore') or not account.get('_id'):
					print 'Missing-id', account['business_name']
					continue
				sc_server.pro_index_id[account['_id']] = account
		except Exception as e:
			print type(e), e
		finally:
			if (fp): fp.close()

		print 'Professional Index: %d entries' % len(sc_server.pro_list)
		return sc_server.pro_index_id



#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################
