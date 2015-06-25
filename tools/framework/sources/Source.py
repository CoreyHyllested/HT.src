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

import sys, os, time
import urllib2, requests
import json, random
from pprint import pprint as pp
from controllers import *
from models import *



class Source(object):
	USE_WEBCACHE = False
	SECONDS = 90	# get from robots.txt
	SOURCE_TYPE	= 'UnknownSource'
	errors = {}
	ratelimited = []

	def __init__(self):
		self.companies = None
		self.doc_companies = None
		self.co_index = None
		self.doc_scrapemap = {}
		self.doc_invaliddirs = []		# populated in __update_directory
	
	def __repr__(self):	return '<%r>'% (self.SOURCE_TYPE)
	def __str__(self):	return '<%r>'% (self.SOURCE_TYPE)


	def __build_company_index(self, save_index):
		company_lst = self.companies
		company_idx	= {}
		duplicates	= []

		for business in company_lst:
			# companies not using proper format are ignored, deleted on write
			if (business.get('_id_' + self.source_type()) == None):	continue
			if not company_idx.get(business['_id_' + self.source_type()]):
				company_idx[business['_id_' + self.source_type()]] = business
			else:
				duplicates.append(business)

		if (save_index): self.co_index = company_idx
		self.companies = company_idx.values()
		print '%s.read_company_cache(%d|%d dupes|%d companies)' % (self.SOURCE_TYPE, len(company_lst), len(duplicates), len(self.companies))



	def __read_companies_cache(self, update, save_index, dump_results=False):
		self.companies	= []
		self.doc_companies = Document('companies.json', self, doc_type=DocType.JSON_METADATA)
		self.doc_companies.location = self.get_source_directory()
		self.doc_companies.filename = 'companies.json'
		self.doc_companies.read_cache(debug=False)
		self.companies	= json.loads(self.doc_companies.content)
		self.__build_company_index(update or save_index)
		if (dump_results): pp(self.companies)


	def save_company_directory(self):
		print '%s.update_companies_dir; writing %d entries' % (self.SOURCE_TYPE, len(self.co_index.values()))
		self.doc_companies.backup()
		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()


	def source_type(self):
		return self.SOURCE_TYPE.lower()

	def get_source_directory(self):
		return os.getcwd() + '/data/sources/' + self.source_type() + '/'

	def get_source_cache_directory(self):
		return os.getcwd() + '/data/sources/' + self.source_type() + '/cache/'

	def get_company_index(self):
		self.get_company_directory(False, save_index=True)
		return self.co_index

	def get_company_directory(self, update=False, save_index=False):
		if (self.companies is None or (save_index and not self.co_index)):
			self.__read_companies_cache(update, save_index)

		# if update, move and save old copy
		if (update or len(self.companies) == 0):
			self.companies = []	# reset, will need to remove this.
			self.update_company_directory()
		return self.companies


	def create_source_document(self, uri, document_type):
		doc = Document(uri, self, doc_type=document_type)
		doc.location = self.get_source_cache_directory() + url_clean(uri)
		return doc


	def scrape_document(self, document):
		if (document is None or document.content is None): return 0

		scrape = self.doc_scrapemap[document.doc_type]
		if (scrape is None): raise Exception('BUG: scrape function doesn\'t exist')
		return scrape(self, document)



	def sleep(self, secs=None):
		if (not secs): secs = self.SECONDS + random.randint(0, 10)
		time.sleep(secs)


	def add_error(self, error_class, name):
		err_array = self.errors.get(error_class, [])
		err_array.append(name)
		self.errors[error_class] = err_array
		self.dump_errors()	#remove eventually

	def dump_errors(self):
		pp(self.errors)



	def uri_exists_in_directory(self, uri):
		doc_exists = False
		for document in self.directories:
			if document.uri == uri:
				doc_exists  =  True
				break
		if (not doc_exists):
			# add uri to 'SHOULD BE ON' directory/array
			print '\n\nADD ANOTHER DIRECTORY: ', '"' + uri.replace('Boulder.CO', 'LOCATION') + '",'



	def transform_companies(self, backup=True):
		print '%s.transform_companies(): backup? %r' % (self.SOURCE_TYPE, backup)
		self.get_company_index()
		self.doc_companies.backup()
		rewrite = self.doc_scrapemap.get('rewrite')
		if (rewrite): rewrite(self)



	def normalize_email(self, email_address, company):
		emails = company.get('business_emails', [])
		if (emails): emails.append(email_address)
		company['business_emails'] = emails


	def normalize_phone(self, phone, company):
		phones = company.get('business_phones', [])
		if (phone):
			# compare: business_phones[idx].national_number
			# display: phonenumbers.format_number(business_phones.idx.national_number, PhoneNumberFormat.NATIONAL)?
			phones.append(phonenumbers.parse(phone, 'US').national_number)
		company['business_phones'] = phones


	def normalize_website(self, website, company):
		if (website): website = urltools.normalize(website.lower())
		company['business_website'] = website


