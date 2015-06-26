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


import uuid, copy
import re, random, time, json
import urltools, phonenumbers
from json	import JSONEncoder 
from pprint	import pprint as pp
from datetime	import datetime as dt 
from Levenshtein import distance
from controllers import filesystem, url_tools



class Business(object):
	def __init__(self, b_dictionary, source=None, index=False):
		self._id				= None
		self.business_name		= None
		self.business_website	= None
		self.business_phones	= []
		self.business_emails	= []
		self.location_ids		= []
		self.sources	= []
		self.collisions = {}				# when added to index
		self.update(b_dictionary, checked=False)

		if (not self._id): self._id = str(uuid.uuid4())
		if (self.__dict__.get('chain_id')):
			print 'CHAIN %s %s %s' % (self.business_name, self.chain_id, self._id_factual)

		# add location (from source list)
		if (b_dictionary.get('address')):
			bus_location = BusinessLocation(b_dictionary.get('address'), self)
			self.location_ids.append(bus_location._id)
		self.__remove_attrs()


	def __remove_attrs(self):
		if (self.__dict__.get('address')):	del self.address
		if (self.__dict__.get('hours')):	del self.hours
		if (self.__dict__.get('_id_factual')): del self._id_factual


	def contact_phone(self):	return self.business_phones
	def contact_email(self):	return self.business_emails
	def get_location_ids(self):	return self.location_ids
	def get_collisions(self):	return self.collisions
	def get_sources(self):	return self.sources
	def get_webaddr(self):	return url_tools.normalize_webaddr(self.business_website)

	def get_all_locations(self):
		rc = []
		for location_id in self.location_ids:
			location = BusinessLocation.get_location(location_id)
			if (location is None):
				print location_id
				raise Exception ('WTF is this null?')
			rc.append(location)
		return rc

	def get_location_id(self):
		# expect exactly one location_id; throw excpetion on any other outcome.
		if (len(self.location_ids) != 1): raise Exception("More than one (or zero) location exists")
		return self.location_ids[0]

	def get_location(self):
		return BusinessLocation.get_location(self.get_location_id())


	def match_website_index(self, index, collisions):
		match = index.get(self.get_webaddr())
		if (self.get_webaddr() and match):
			collisions.append( (match._id, 'website', match.business_name) )
			return match.add_collision(self, 'website')
		return False


	def match_address_index(self, index, collisions):
		for location in self.get_all_locations():
			match = index.get(location.street)
			if (match):
				collisions.append( (match._id, 'address', match.business_name) )
				return match.add_collision(self, 'address')
		return False


	def match_names_index(self, index, collisions):
		match = index.get(self.business_name)
		if (match):
			collisions.append( (match._id, 'name', match.business_name) )
			return match.add_collision(self, 'name')
		return False


	def match_phone_index(self, index, collisions): 
		for phone in self.contact_phone():
			match = index.get(phone)
			if (match):
				collisions.append( (match._id, 'phone', match.business_name) )
				return match.add_collision(self, 'phone')
		return False


	def match_email_index(self, index, collisions):
		for email in self.contact_email():
			match = index.get(email)
			if (match):
				collisions.append( (match._id, 'email', match.business_name) )
				return match.add_collision(self, 'email')
		return False


	def add_collision(self, match, type):
		# Heads up, the logic is reversed
		# The master list (i.e. SELF) has pointer to non-business
		similarity = {}
		self.define_similarity(match, similarity, type)
		self.collisions[match.get_sources()[0]['id']] = similarity
		return True


	def define_similarity(self, b, same, matched_on):
		same['type'] = matched_on
		same['name'] = b.get_sources()[0]['name']
		same['id']	 = b.get_sources()[0]['id']

		attr = {}
		attr['name']  = distance(self.business_name, b.business_name)
		attr['website'] = None
		attr['address'] = None	# really, street & city
		attr['phone']	= None
		attr['email']	= None

		if self.business_website and b.business_website:
			attr['website'] = False
			if self.business_website == b.business_website: attr['website'] = True
		if (len(self.get_all_locations()) and len(b.get_all_locations())):
			attr['address'] = []
			for this_location in self.get_all_locations():
				for that_location in b.get_all_locations():
					if this_location.street == that_location.street and this_location.city == that_location.city:
						attr['address'].append( (this_location.street, this_location.city) )
		if (len(self.contact_phone()) and len(b.contact_phone())):
			attr['phone'] = []
			for phone in self.contact_phone():
				if phone in b.contact_phone(): attr['phone'].append(phone)
		if (len(self.contact_email()) and len(b.contact_email())):
			attr['email'] = []
			for email in self.contact_email():
				if email in b.contact_email(): attr['email'].append(email)
		same['attr'] = attr



	# merging requires manual intevention
	# an admin adds 'merge'; id & operations to json
	def merge_attributes(self, index, company_dict):
		merge = self.__dict__.get('merge')
		if (not merge): return

		business_id	= merge['id']
		operations	= merge['operations']
		business = index.get(business_id)
		if (not business): raise Exception('Merging w/ non-business %s' % business_id)
		for operation in operations:
			if operation == 'add_location':
				location = BusinessLocation(company_dict.get('address'), business)
				business.location_ids.append(location._id)
				del business.collisions[self.sources[0]['id']]

				# add location to the master list of locations.
				BusinessIndex.master_addr[location._id] = location
			company_dict['_status'] = 'merged'
		if company_dict.get('merge'): del company_dict['merge']
		company_dict['_id'] = business_id
		#print 'MERGING:\n\t%s.%s %s\n\t%s.%s %s' % (self._id, self.business_name, self.business_website, business._id, business.business_name, business.business_website)


	def update(self, b_dictionary, checked=True):
		if (not checked):
			self.__dict__.update(b_dictionary)
			return

		contested = self.__dict__.get('contested', [])
		for k, v in b_dictionary.items():
			if (k == '_id'):
				print 'Word, id exists now?', k, v
			if (k == 'business_id'): continue
			if (k == 'phone'): continue
			#if (k == 'src_logo'): continue	#ignore
			if (self.__dict__.get(k) == None): 
#				print 'CAH %s adding [%r => %r]' % (self.business_id, k, v)
				self.__dict__[k] = v
			elif (self.__dict__.get(k) != v):
				#dist = distance(self.__dict__.get(k), v)
			#	print 'CAH %s.%s' % (self.business_id, k)
			#	print '%r' % (self.__dict__.get(k))
			#	print '%r' % (v)
				contested.append((k, v))
				self.contested = contested




def merge_candidate_website(b, company_list):
	""" return true on merge"""
	for company in company_list:
		rc = mc_website_compare_phones(b, company)
		if (rc): pass	# return
	return False


def mc_website_compare_phones(b1, b2):
	b1_addr = b1.address['street']
	b2_addr = b2.address['street']

	if b1_addr == b2_addr:
		# website and address match.
		#print 'Moonshot. website.addr', (b1._id_factual, b2._id_factual)
		return (b1._id, b2._id)

	for b1_phone in b1.business_phones:
		for b2_phone in b2.business_phones:
			if b1_phone == b2_phone:
				if b1_addr == b2_addr:
					#print 'We GOT ONE!!!, phone/addr', (b1._id_factual, b2._id_factual)
					return (b1._id, b2._id)
				else:
					#print 'potential multi-location. phone w/ different addrs', (b1._id_factual, b2._id_factual)
					#flag?
					pass
	return False



class BusinessLocation(object):
	location_index = {}

	def __init__(self, location_dict, business=None):
		self._id	= None
		self._bid	= business._id if business else None
		self.city	= None
		self.street	= None
		self.state	= None
		self.suite	= None
		self.post	= None

		self.hours	= None
		self.sources = None
		self.contact = {}

		self.__dict__.update(location_dict)

		if (not self._bid):	raise Exception("No business id")
		if (not self._id):	self._id = str(uuid.uuid4())
		if (business):
			if business.__dict__.get('hours'):
				self.hours = ''
				for src_hours in business.hours:
					self.hours = self.hours + src_hours.values()[0]
			self.contact['phone'] = business.contact_phone()
			self.contact['email'] = business.contact_email()
			self.sources = business.sources
		BusinessLocation.location_index[self._id] = self


	@staticmethod
	def get_location_index():
		return BusinessLocation.location_index

	@staticmethod
	def get_location(id):
		return BusinessLocation.location_index.get(id)


class BusinessIndex(object):
	idx_source	= {}
	idx_website = {}
	idx_address	= {}
	idx_phone	= {}
	idx_email	= {}
	idx_names	= {}

	master_bidx = {}
	master_addr	= {}

	src_collisions = []

	def __init__(self):
		self.master_list_path = 'data/companies.json'
		self.__load_company_list(self.master_list_path)
		self.__index_master_list()


	def __load_company_list(self, file_path, source=None, debug=False):
		content = filesystem.read_file(file_path, debug)
		self.businesses	= content['businesses']
		self.locations	= content['locations']
		if (debug): print 'Loaded company list: %d in size' % (len(content))
		return content


	def __save_master_file(self, file_path, debug=False):
		if (debug): print 'saving company list: %d in size' % (len(BusinessIndex.master_bidx))
		complete = {}
		complete['businesses']	= BusinessIndex.master_bidx.values()
		complete['locations']	= BusinessIndex.master_addr.values()
		filesystem.write_file(file_path, json.dumps(complete, cls=BusinessEncoder, indent=4, sort_keys=True))



	def __index_master_list(self):
		for business_dict in self.businesses:
			b = Business(business_dict)
			if (not b._id): raise Exception ('WTF, no _id')
			BusinessIndex.master_bidx[b._id] = b
			BusinessIndex.idx_names[b.business_name] = b
			BusinessIndex.idx_website[b.get_webaddr()] = b
			for phone in b.contact_phone():
				BusinessIndex.idx_phone[phone] = b
			for email in b.contact_email():
				BusinessIndex.idx_email[email] = b

		for location_dict in self.locations:
			location = BusinessLocation(location_dict)
			BusinessIndex.master_addr[location._id] = location
			business = BusinessIndex.get_business(location._bid)
			if (not business):
				print location._bid
				raise Exception('WTF - business does not exist')
			BusinessIndex.idx_address[location.street] = business
		print 'Master List: businesses %d, locations %d' % (len(BusinessIndex.master_bidx), len(BusinessIndex.master_addr))
		print 'Indexed websites(%d) Phones(%d) Emails(%d)' % (len(BusinessIndex.idx_website), len(BusinessIndex.idx_phone), len(BusinessIndex.idx_email))


	def save(self):
		print 'Writing master list. Businesses %d, locations %d collisions %d' % (len(BusinessIndex.master_bidx), len(BusinessIndex.master_addr), len(BusinessIndex.src_collisions))
		print 'Indexed websites(%d) Phones(%d) Emails(%d)' % (len(BusinessIndex.idx_website), len(BusinessIndex.idx_phone), len(BusinessIndex.idx_email))
		self.__save_master_file(self.master_list_path, debug=True)



	@staticmethod
	def add_source(source, params):
		if (params.source) and (params.source != source.SOURCE_TYPE): return
		BusinessIndex.idx_source[source.source_type()] = {}

		directory = source.get_company_directory(save_index=True)
		source_id = '_id_' + source.source_type()

		print 'Business.add_source\t%s\t%d' % (source.source_type(), len(directory))
		src_businesses = []
		for company in directory:
			try:
				b = BusinessIndex.create_business(company)
			except Exception as e:
				#print type(e), e
				continue
			if (not b): continue

			src_businesses.append(b)
			if (BusinessIndex.index_business(b)):
				company['_id'] = b._id
			else:
				b.merge_attributes(BusinessIndex.master_bidx, company)
				#BusinessIndex.src_collisions.append(b.collsions)

		#for c in BusinessIndex.src_collisions:
		#	pp (c)

		source.save_company_directory()
		return



	@staticmethod
	def create_business(business_dict):
		# all businesses -- must -- have a name.
		if (business_dict.get('_ignore')):
			print business_dict['_ignore']
			raise Exception('IgnoreBusiness')
		if (not business_dict['business_name']):
			raise Exception('No Name')

		id = business_dict.get('_id')
		if (id and BusinessIndex.master_bidx.get(id)):
			raise Exception('Exists')
			return None

		b = Business(business_dict)
		for source in b.get_sources():
			src_id		= source['id']
			src_name	= source['name']
			BusinessIndex.idx_source[src_name][src_id] = True
		return b


	@staticmethod
	def index_business(b):
		collisions = []
		b.match_website_index(BusinessIndex.idx_website, collisions)
		b.match_address_index(BusinessIndex.idx_address, collisions)
		b.match_phone_index(BusinessIndex.idx_phone, collisions)
		b.match_email_index(BusinessIndex.idx_email, collisions)
		b.match_names_index(BusinessIndex.idx_names, collisions)
		if (collisions):
			print 'collision', collisions
			return False

		BusinessIndex.master_bidx[b._id] = b
		BusinessIndex.master_addr[b.get_location_id()] = b.get_location()
		BusinessIndex.idx_names[b.business_name] = b
		if (b.get_webaddr()):
			BusinessIndex.idx_website[b.get_webaddr()] = b
		for location in b.get_all_locations():
			BusinessIndex.idx_address[location.street] = b
		for phone in b.contact_phone():
			BusinessIndex.idx_phone[phone] = b
		for email in b.contact_email():
			BusinessIndex.idx_email[email] = b
		return True

	@staticmethod
	def get_business(id):
		return BusinessIndex.master_bidx.get(id)


class BusinessEncoder(JSONEncoder):
	def default(self, obj):
		return obj.__dict__

