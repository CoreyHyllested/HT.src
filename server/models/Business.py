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
	#bus_address	= Column(String(40), ForeignKey('location.location_id'), nullable=True)
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


	def __init__(self, name, location_id, phone=None, email=None, website=None, id=str(uuid.uuid4())):
		print 'Business: init \'' + '\''
		self.bus_id		 = id
		self.bus_name	 = name
		#self.bus_address = location_id
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
#			'business_addr'	: self.bus_address
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
				business = Business.get_json_index().get(bus_id)
				# convert to Business Object
				business['from_json'] = True
		return business



	@staticmethod
	def import_from_json(bus_id):
		json_object = Business.get_json_index().get(bus_id)
		address	= json_object['address']
		website	= json_object.get('business_website')
		phones	= json_object.get('business_phones')
		emails	= json_object.get('business_emails')

		location = Location(address['street'],
							address['suite'],
							address['city'],
							address['state'],
							address['post'],
							address['meta']['lat'],
							address['meta']['lng'])

		contact_phone = phones[0] if phones else None
		contact_email = emails[0] if emails else None

		business = Business(json_object['business_name'],
							location.location_id,
							phone=contact_phone,
							email=contact_email,
							website=website,
							id=json_object['_id'])
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
