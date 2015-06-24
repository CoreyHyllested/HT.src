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


import uuid
import re, random, time, json
import urltools, phonenumbers
from json	import JSONEncoder 
from pprint	import pprint as pp
from datetime	import datetime as dt 
from Levenshtein import distance
from controllers import filesystem, url_tools




class Business(object):
	bus_list	= []

	resolve		= {	'factual' : {}	}
	idx_source	= {	'factual' : {}	}

	idx_website	= {}
	idx_street	= {}
	idx_phone	= {}
	idx_email	= {}
	idx_names	= {}


	def __init__(self, b_dictionary, source=None, index=False):
		self._id				= None
		self.business_name		= None
		self.business_website	= None
		self.business_phones	= []
		self.business_emails	= []
		self.sources	= [] 				#[ source ] if source else []
		self.collisions = []				# when added to index
		self.update(b_dictionary, checked=False)

		if (not self._id): self._id = str(uuid.uuid4())
		if (self.__dict__.get('chain_id')):
			print 'CHAIN %s %s %s' % (self.business_name, self.chain_id, self._id_factual)

	def contact_phone(self):	return self.business_phones
	def contact_email(self):	return self.business_emails
	def get_collisions(self):	return self.collisions
	def get_sources(self):	return self.sources
	def get_webaddr(self):	return url_tools.normalize_webaddr(self.business_website)



	def oldthing(b, src, src_id):
		# add business to two main lists
		Business.idx_source[src][src_id] = b
		Business.resolve[src][src_id] = {}
		#if (merge_candidate_website(b, companies)): return

	def match_website_index(self, index):
		match = index.get(self.get_webaddr())
		if (self.get_webaddr() and match):
			self.add_index_collision(match, 'website')

	def match_address_index(self, index):
		match = index.get(self.address.get('street'))
		if (self.address.get('street') and match):
			self.add_index_collision(match, 'address')

	def match_phone_index(self, index):
		for phone in self.contact_phone():
			match = index.get(phone)
			if (match): self.add_index_collision(match, 'phone')

	def match_email_index(self, index):
		for email in self.contact_email():
			match = index.get(email)
			if (match): self.add_index_collision(match, 'email')

	def add_index_collision(self, match, type):
		self.collisions.append( (match._id, type, match.business_name, match.get_webaddr(), match.address.get('street'), match.contact_phone(), match.contact_email()) )


	def merge (self, business, why):
		print 'MERGING (matched on %s):\n\t%s.%s %s\n\t%s.%s %s' % (why, self.source, self.name, self.business_www, business.sources, business.name, business.business_www)
		pass


	def update(self, b_dictionary, checked=True):
		if (not checked):
			self.__dict__.update(b_dictionary)
			return

		contested = self.__dict__.get('contested', [])
		for k, v in b_dictionary.items():
			#print 'k =', k, v
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




class BusinessIndex(object):
	idx_source	= {}
	idx_website = {}
	idx_address	= {}
	idx_phone	= {}
	idx_email	= {}
	master_bidx = {}

	def __init__(self):
		master_list_path = 'data/companies.json'
		self.master_list = self.__load_company_list(master_list_path)
		self.__index_master_list(self.master_list)


	def __load_company_list(self, file_path, source=None, debug=False):
		content = filesystem.read_file(file_path, debug)
		if (debug): print 'Loaded company list: %d in size' % (len(content))
		return content


	def __index_master_list(self, companies):
		for business_dict in companies:
			b = Business(business_dict)
			if (not b._id): raise Exception ('WTF, no _id')
			BusinessIndex.master_bidx[b._id] = b
			BusinessIndex.idx_website[b.get_webaddr()] = b
			BusinessIndex.idx_address[b.address.get('street')] = b
			for phone in b.contact_phone():
				BusinessIndex.idx_phone[phone] = b
			for email in b.contact_email():
				BusinessIndex.idx_email[email] = b
		print 'Master List: %d' % (len(BusinessIndex.master_bidx))
		print 'Indexed websites(%d) Phones(%d) Emails(%d)' % (len(BusinessIndex.idx_website), len(BusinessIndex.idx_phone), len(BusinessIndex.idx_email))



	@staticmethod
	def add_source(source, params):
		if (params.source) and (params.source != source.SOURCE_TYPE): return
		BusinessIndex.idx_source[source.source_type()] = {}

		directory = source.get_company_directory()
		source_id = '_id_' + source.source_type()

		print 'Business.add_source\t%s\t%d' % (source.source_type(), len(directory))
		src_businesses = []
		src_collisions = []
		for company in directory[0:1000]:
			b = BusinessIndex.create_business(company)
			if (BusinessIndex.index_business(b)):
				src_businesses.append(b)
			else:
				src_collisions.append(b)


		print 'Master List: %d collisions(%d)' % (len(BusinessIndex.master_bidx), len(src_collisions))
		print 'Indexed websites(%d) Phones(%d) Emails(%d)' % (len(BusinessIndex.idx_website), len(BusinessIndex.idx_phone), len(BusinessIndex.idx_email))

		for src in Business.resolve.keys():
			print 'INSPECTING Websites:', len(BusinessIndex.idx_website.keys())
			for website in BusinessIndex.idx_website.keys():
				b = BusinessIndex.idx_website[website]
				#print website, b._id, b.get_sources()[0]['id']

			print 'Phonebook sz', len(BusinessIndex.idx_phone)
			for phone in BusinessIndex.idx_phone.keys():
				#sz = len(BusinessIndex.idx_phone[phone])
				#	for b in BusinessIndex.idx_phone[phone]:
						#print sz, phone, b.business_phones, b.categories[0].get('factual'), b.business_name
				pass
		return



	@staticmethod
	def create_business(business_dict):
		# business --must-- have a name
		if (not business_dict['business_name']):
			raise Exception('No name')

		id = business_dict.get('_id')
			
		b = Business(business_dict)
		for source in b.get_sources():
			src_id		= source['id']
			src_name	= source['name']
			BusinessIndex.idx_source[src_name][src_id] = True
		return b


	@staticmethod
	def index_business(b):
		b.match_website_index(BusinessIndex.idx_website)
		b.match_address_index(BusinessIndex.idx_address)
		b.match_phone_index(BusinessIndex.idx_phone)
		b.match_email_index(BusinessIndex.idx_email)
		if (b.get_collisions()):
			print 'Had Collisions', len(b.get_collisions())
			return False

		print 'No collisions add to main index'
		BusinessIndex.master_bidx[b._id] = b
		if (b.get_webaddr()):
			BusinessIndex.idx_website[b.get_webaddr()] = b
		for phone in b.contact_phone():
			BusinessIndex.idx_phone[phone] = b
		for email in b.contact_email():
			BusinessIndex.idx_email[email] = b
		return True


	@staticmethod
	def save():
		pass
		#save	master_index
		#update source_index





class BusinessEncoder(JSONEncoder):
	def default(self, obj):
		return obj.__dict__


