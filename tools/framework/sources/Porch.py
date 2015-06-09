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

from Source import *
from pprint import pprint as pp
from bs4 import BeautifulSoup, Comment
from models import *
from controllers import *



class Porch(Source):
	SOURCE_TYPE	= 'Porch'

	def __init__(self, ua, queue=None):
		super(Porch, self).__init__()
		self.ua = ua
		self.directories = []
		self.doc_directories = None
		self.doc_scrapemap = self.PORCH_SCRAPEMAP


	def __load_directory_of_directories(self):
		file_path	= self.get_source_directory() + '/directories.json'
		file_json	= self.read_json_file(file_path)
		self.doc_invaliddirs = file_json.get('invalid_directories')
		for directory in file_json.get('directories'):
			base = 'https://porch.com/search/results?q=%s&loc=Boulder, CO&zip=80302&lat=40.0149856&lon=-105.27054559999999&view=list&offset=%d'
			for offset in xrange(10):
				url = base % (directory, 10*offset)
				if (url in self.doc_invaliddirs): break
				directory_doc = self.create_source_document(url, DocType.PORCH_DIRECTORY)
				self.directories.append(directory_doc)


	def __scrape_business(self, document):
		print '%s.scrape_business(%s)' % (self.SOURCE_TYPE, document.location)


	def __scrape_directory(self, document):
		#print '%s.scrape_directory(%s)' % (self.SOURCE_TYPE, document.location)
		return
		# scrape 15 companies, available info... name, URL, phone #
		# add to self.companies
		document_soup	= BeautifulSoup(document.content)
		business_list	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_list:
			company = {}
			company_addr = {}

			self.companies.append(company)
		return len(business_list)


	PORCH_SCRAPEMAP = {
		DocType.PORCH_DIRECTORY	: __scrape_directory,
		DocType.PORCH_BUSINESS	: __scrape_business
	}



	def update_company_directory(self):
		print 'Porch.update_directory'
		if (len(self.directories) == 0): self.__load_directory_of_directories()

		for directory in self.directories:
			directory.get_document(debug=False)
			self.scrape_document(directory)

		print 'Porch.update_directory; now contains %d entries' % (len(self.companies))
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()

