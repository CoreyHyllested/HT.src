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



class HomeAdvisor(Source):
	SOURCE_TYPE	= 'HomeAdvisor'

	def __init__(self, ua, queue=None):
		super(HomeAdvisor, self).__init__()
		self.ua = ua
		self.directories = []
		self.doc_directories = None
		self.doc_scrapemap = self.HOMEADV_SCRAPEMAP


	def __load_directory_of_directories(self):
		file_path	= self.get_source_directory() + '/directories.json'
		directories = self.read_json_file(file_path)
		for directory in directories:
			directory = self.__build_directory_uri(directory)
			directory_doc = self.create_source_document(directory, DocType.HOME_DIRECTORY)
			self.directories.append(directory_doc)


	def __build_directory_uri(self, base_uri, update=None):
		# append ?startingIndex=X, increases by 25.
		if (update):
			# ?startingIndex=X => ?startingIndex=update
			idx = base_uri.find('Index=')
			if (idx == -1):	base_uri = '%s?startingIndex=25' % (base_uri)
			else:			base_uri = '%s' % (base_uri[0:-2]) + str(int(base_uri[-2:]) + 25)
		return base_uri.replace('LOCATION', 'Boulder.CO')



	def __scrape_business(self, document):
		print '%s.scrape_business(%s)' % (self.SOURCE_TYPE, document.location)


	def __scrape_directory(self, document):
		#print '%s.scrape_directory(%s)' % (self.SOURCE_TYPE, document.location)
		# scrape up to 25 companies, available info... name, URL, phone #
		document_soup	= BeautifulSoup(document.content)
		business_list	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_list:
			company = {}
			company_addr = {}
			name	= business.find(itemprop='name').get_text()
			phone	= business.find(itemprop='telephone').get_text()
			http	= business.find(itemprop='url').attrs.get('href')
			if (http): http = 'http://www.homeadvisor.com' + http

			addr	= business.find(itemtype='http://schema.org/PostalAddress')
			addrStreet	= addr.find(itemprop='streetAddress').get_text()
			addrCity	= addr.find(itemprop='addressLocality').get_text()
			addrState	= addr.find(itemprop='addressRegion').get_text()
			addrPostal	= addr.find(itemprop='postalCode').get_text()

			rating	= business.find(class_=['t-stars-small-inner'])
			if (rating): rating = rating.attrs['style'].replace('width: ', '').rstrip(';')
			reviews = business.find(class_=['l-small-top-space', 'l-small-bottom-space'])
			if (reviews):
				reviews = reviews.get_text().strip()

				reviews = reviews.replace('Verified Reviews', '')
				reviews = reviews.replace('Verified Review', '')
				if ('Available' in reviews):
					reviews = 0
					if (rating): print 'CHECK it out.  rating w/ reviews? (%s)' % name
				reviews = int(reviews)


			company['name'] = name
			company['phone']			= phone
			company['phone_display']	= phone
			company['src_homeadvisor']	= http
			if (rating):	company['rating']	= rating
			if (reviews):	company['reviews']	= reviews
			if (addr): company['addr'] = {
					"full"		: addrStreet + '\n' + addrCity + ', ' + addrState + ', ' + addrPostal,
					"street"	: addrStreet,
					"city"		: addrCity,
					"state"		: addrState,
					"postal"	: addrPostal
				}


			#pp(company)
			self.companies.append(company)
		if (len(business_list) == 25):
			test_url = self.__build_directory_uri(document.uri, update=True)
			self.uri_exists_in_directory(test_url)
		#print '%s.scrape_directory added %d entries' % (self.SOURCE_TYPE, len(business_list))
		return len(business_list)


	HOMEADV_SCRAPEMAP = {
		DocType.HOME_DIRECTORY	: __scrape_directory,
		DocType.HOME_BUSINESS	: __scrape_business
	}



	def update_company_directory(self):
		print 'HomeAdvisor.update_directory'
		if (len(self.directories) == 0): self.__load_directory_of_directories()

		for directory in self.directories:
			directory.get_document(debug=True)
			self.scrape_document(directory)

		#print 'HomeAdvisor.update_directory; now contains %d entries' % (len(self.companies))
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()

