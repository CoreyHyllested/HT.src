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
		full_path = self.get_source_directory() + '/directories.json'
		directories = self.read_json_file(full_path)
		for directory in directories:
			print directory
			directory = directory.replace('LOCATION', 'Boulder.CO')
			print directory
			directory_doc = self.create_source_document(directory, DocType.HOME_DIRECTORY)
			self.directories.append(directory_doc)

	def __scrape_business(self, document):
		print 'Home.scrape_business(%s)' % (document.location)


	def __scrape_directory(self, document):
		print 'Home.scrape_directory(%s)' % (document.location)
		return
		# scrape 15 companies, available info... name, URL, phone #
		# add to self.companies
		document_soup	= BeautifulSoup(document.content)
		business_list	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_list:
			company = {}
			company_addr = {}

			name	= business.find(itemprop='name')
			http	= name.attrs['href']

			phone	= business.find(itemprop='telephone')
			reviews	= business.find(compid='review')
			if (reviews):
				src_rev	= reviews.attrs['href']
				src_url = reviews.attrs['href'].replace('browseReviews', 'pro')
			else:
				src_url = http
			
			if 'browseReviews' in src_url:
				print 'http:', name.attrs['href']
				if (reviews):
					 print 'reviews.rev = ', src_rev
					 print 'reviews.url = ', src_url
				raise Exception('dammit-browseReviews')

			if 'javascript' in src_url:
				self.add_error('missing_src_url', name.get_text())
				#raise Exception('dammit-javascript')
				
			sponsor	= business.find_all(class_=['text-sponsored'])
			addr	= business.find(itemtype='http://schema.org/PostalAddress')
			addrStreet	= [] #addr.find(itemprop='streetAddress') #.get_text()
			addrCity	= addr.find(itemprop='addressLocality') #.get_text()
			addrState	= addr.find(itemprop='addressRegion') #.get_text()
			addrPostal	= addr.find(itemprop='postalCode') #.get_text()

			# create metadata
			company['name'] = name.get_text()
			if (src_url):	company['src_houzz'] =	src_url
			if (reviews):	company['src_reviews'] = src_rev
			if (phone):	company['phone']			= phone.get_text()
			if (phone):	company['phone_display']	= phone.get_text()
			if (sponsor): company['sponsor_houzz']	= True

			if (addr): 
#				"full"		: addrStreet + '\n' + addrCity + ', ' + addrState,
#				"display"	: addrDisplay
				if (addrCity):		company_addr["city"]	= addrCity.get_text()
				if (addrStreet):	company_addr["street"]	= addrStreet.get_text()
				if (addrState):		company_addr["state"]	= addrState.get_text()
#				company["full"] = addrStreet + '\n' + addrCity + ', ' + addrState,
#				"display"	: addrDisplay
				company["addr"] = company_addr

			self.companies.append(company)
			#if (len(self.companies) % 250 == 0): pp(company)
		return len(business_list)


	HOMEADV_SCRAPEMAP = {
		DocType.HOME_DIRECTORY	: __scrape_directory,
		DocType.HOME_BUSINESS	: __scrape_business
	}



	def update_company_directory(self):
		print 'HomeAdvisor.update_co_directory'
		if (len(self.directories) == 0): self.__load_directory_of_directories()

		for directory in self.directories:
			print 'Home.update_directory\tget_document(%r)' % (directory)
			directory.get_document(debug=True)
			self.scrape_document(directory)

		print 'Home.company listing - done'
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()

