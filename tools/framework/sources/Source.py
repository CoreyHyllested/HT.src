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
	
	def __repr__(self):	return '<%r>'% (self.SOURCE_TYPE)
	def __str__(self):	return '<%r>'% (self.SOURCE_TYPE)


	def read_companies_cache(self, dump_results=False):
		self.doc_companies = Document('companies.json', doc_type=DocType.JSON_METADATA)
		self.doc_companies.location = self.get_source_directory()
		self.doc_companies.filename = 'companies.json'
		self.doc_companies.read_cache(debug=True)
		self.companies = json.loads(self.doc_companies.content)
		print '%s.read_company_cache(%d companies)' % (self.SOURCE_TYPE, len(self.companies))
		if (dump_results): pp(companies)


	def get_source_directory(self):
		return os.getcwd() + '/data/sources/' + self.SOURCE_TYPE.lower() + '/'

	def get_source_cache_directory(self):
		return os.getcwd() + '/data/sources/' + self.SOURCE_TYPE.lower() + '/cache/'


	def create_source_document(self, uri, document_type):
		doc = Document(uri, doc_type=document_type)
		doc.location = self.get_source_cache_directory() + url_clean(uri)
		return doc


	def sleep(self, secs=None):
		if (not secs):
			secs = self.SECONDS + random.randint(0, 10)
		#print '%s.update_co_directory: (downloaded) so sleeping (%d)...' % (self.SOURCE_TYPE, seconds)
		time.sleep(secs)


	def add_error(self, error_class, name):
		err_array = self.errors.get(error_class, [])
		err_array.append(name)
		self.errors[error_class] = err_array
		self.dump_errors()	#remove eventually

	def dump_errors(self):
		pp(self.errors)


	def read_json_file(self, rel_file_path, DEBUG=False):
		# FOR TESTING.  http://jsonlint.com/
		try:
			file_pointer = open (os.getcwd() + rel_file_path, 'r')
			file_content = file_pointer.read()
			json_content = json.loads(file_content)
			if (DEBUG): pp(json_content)
			#directory = data.get('directory', [])
			return json_content
		except Exception as e:
			print str(e)
		finally:
			if (file_pointer): file_pointer.close()
		return { "data" : None }

