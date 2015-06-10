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
	SECONDS	= 60

	def __init__(self, queue=None):
		super(HomeAdvisor, self).__init__()
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
		document_soup	= BeautifulSoup(document.content)
		business_list	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_list:
			http = business.find(itemprop='url').attrs.get('href')
			if (http): http = 'http://www.homeadvisor.com' + http

			company = self.co_index.get(http, {})

			business_address = business.find(itemtype='http://schema.org/PostalAddress')
			self.__scrape_directory_addr(business_address, company)
			self.__scrape_directory_rating(business, company)

			company['name'] 			= business.find(itemprop='name').get_text()
			company['phone_display']	= business.find(itemprop='telephone').get_text()
			company['phone']			= re.sub('[ +()-.,]', '', company['phone_display'])
			company['id_homeadvisor']	= http[http[0:-5].rfind('.')+1:-5]
			company['src_homeadvisor']	= http
			self.co_index[http] = company

		if (len(business_list) == 25):
			test_url = self.__build_directory_uri(document.uri, update=True)
			self.uri_exists_in_directory(test_url)
		return len(business_list)



	def __scrape_directory_addr(self, addr_soup, company):
		if (not addr_soup): return

		addrStreet	= addr_soup.find(itemprop='streetAddress').get_text()
		addrCity	= addr_soup.find(itemprop='addressLocality').get_text()
		addrState	= addr_soup.find(itemprop='addressRegion').get_text()
		addrPostal	= addr_soup.find(itemprop='postalCode').get_text()

		addr = company.get('addr', {})
		if (addrStreet):	addr['street'] = addrStreet
		if (addrCity):		addr['city'] = addrCity
		if (addrState):		addr['state'] = addrState
		if (addrPostal):	addr['post'] = addrPostal
		company['addr'] = addr


	def __scrape_directory_rating(self, business_soup, company):
		rating	= business_soup.find(class_=['t-stars-small-inner'])
		if (rating): company['rating_homeadvisor']	= rating.attrs['style'].replace('width: ', '').rstrip(';')

		reviews = business_soup.find(class_=['l-small-top-space', 'l-small-bottom-space'])
		if (reviews):
			reviews = reviews.get_text().strip()
			reviews = reviews.replace('Verified Reviews', '')
			reviews = reviews.replace('Verified Review', '')
			if ('Available' in reviews): reviews = 0
			company['reviews_homeadvisor']	= int(reviews)


	HOMEADV_SCRAPEMAP = {
		DocType.HOME_DIRECTORY	: __scrape_directory,
		DocType.HOME_BUSINESS	: __scrape_business
	}



	def update_company_directory(self):
		if (len(self.directories) == 0): self.__load_directory_of_directories()
		print '%s.update_companies, %d directories' % (self.SOURCE_TYPE, len(self.directories))

		for directory in self.directories:
			directory.get_document(debug=False)
			self.scrape_document(directory)

		print '%s.update_companies; %d entries' % (self.SOURCE_TYPE, len(self.co_index.values()))
		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()
		self.companies = self.co_index.values()

