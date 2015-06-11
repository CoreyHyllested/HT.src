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


class Business(object):
	def __init__(self, b_dictionary, source=None):
		#print 'Creating business'
		self.name	= None
		self.business_phone	= None
		self.business_www	= None
		self.business_id	= None
		self.phone	= None
		self.source	= source

		self.update(b_dictionary, checked=False)

		if (self.business_id == None):
			self.business_id = str(uuid.uuid4())

		# business --must-- have a name
		if (not self.name):
			pp(b_dictionary)
			raise Exception('No name')

		self.__normalize_phone()
		self.__normalize_www()


	def __normalize_phone(self):
		if (not self.phone): return
		normalized = phonenumbers.parse(self.phone, 'US')
		self.business_phone		= normalized.national_number
		self.phone_normalized	= normalized
		#phonenumbers.format_number(, phonenumbers.PhoneNumberFormat.NATIONAL)

	def __normalize_www(self):
		if (not self.business_www): return
		self.business_www = urltools.normalize(self.business_www)


	def merge (self, business, why):
		print 'MERGING (matched on %s):\n\t%s.%s %s\n\t%s.%s %s' % (why, self.source, self.name, self.business_www, business.source, business.name, business.business_www)
		pass

	def update_attr(self, key, value):
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




class BusinessIndex(object):

	def __init__(self, name):
		self.index = {}
		self.idx_name	= {}
		self.idx_www	= {}
		self.idx_phone	= {}
		self.merge_manual	= []
		self.merge_autom	= []
		self.name = name


	def insert(self, business):
		if not business: return None

		# check if matches phone.
		insert_name		= business.__dict__.get('name')
		insert_phone	= business.__dict__.get('phone')
		insert_web		= business.__dict__.get('src_www')

		phone_match_id	= self.idx_phone.get(insert_phone)
		www_match_id	= self.idx_www.get(insert_web)
		if (phone_match_id):
			phone_match_co	= self.index[phone_match_id]
			name_dist = distance(insert_name, phone_match_co.name)

			if (name_dist == 0 or (www_match_id == phone_match_id)):
				#print 'Merging! [' + str(insert_name) + '] with [' + str(phone_match_co.name) + ']\t', name_dist
				phone_match_co.update(business.__dict__)
				self.merge_autom.append( str(business.business_id) + " " + str(business.name)  ) 
				return
			elif (name_dist > 0):
				self.merge_manual.append( (phone_match_id, business.business_id, business.name) )
			
		self.index[business.business_id] = business
		self.idx_phone[insert_phone]	= business.business_id
		self.idx_www[insert_web]	= business.business_id
		self.idx_name[insert_name]	= business.business_id
		#print 'added', business.business_id, business.__dict__.get('phone')

	def get_list(self):
		companies = []	
		for k in self.index.keys():
			companies.append(self.index.get(k))
		return companies


class BusinessEncoder(JSONEncoder):
	def default(self, obj):
		return obj.__dict__


