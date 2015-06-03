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



class Houzz(Source):
	SOURCE_TYPE	= 'Houzz'

	def __init__(self, ua, queue=None):
		super(Houzz, self).__init__()
		self.ua = ua


	def __read_companies_cache(self, dump_results=False):
		self.doc_companies = Document('companies.json', doc_type=DocType.JSON_METADATA)
		self.doc_companies.location = self.get_source_directory()
		self.doc_companies.filename = 'companies.json'
		self.doc_companies.read_cache(debug=True)
		self.companies = json.loads(self.doc_companies.content)
		if (dump_results): pp(companies)



	def houzz_scrape_document(self, document):
		if (document is None): return None
		if (document.content is None): return None

		if (document.doc_type == DocType.HOUZ_DIRECTORY):
			nr = self.houzz_scrape_directory(document)
		if (document.doc_type == DocType.HOUZ_BUSINESS):
			nr = self.houzz_scrape_business(document)



	def houzz_scrape_business(self, document):
		print 'Houzz.scrape_business(%s)' % (document.location)


	def houzz_scrape_directory(self, document):
		print 'Houzz.scrape_directory(%s)' % (document.location)
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

#			image	= business.find_all(itemtype='http://schema.org/ImageObject')
#			yelurl	= business.find_all(itemprop='name')[0].attrs.get('href')
#			links	= business.find_all(class_=['link', 'newtab'])

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

#			if len(image) > 0:
#				logo = image[0].attrs.get('src')
#				company['src_logo'] = logo

#			for uri in links:
#				URI = uri.attrs.get('href')
#				if (('maps.google.com' not in URI) and ('www.yelp.com' not in URI)):
#					company['http'] = URI
			self.companies.append(company)
			if (len(self.companies) % 50 == 0): 
				print 'company list:', len(self.companies)
				pp(company)
		return len(business_list)





	def update_company_directory(self):
		print 'Houzz.update_co_directory'

		total_results = 46824	 #total joke, but there it is.
		base = 'http://www.houzz.com/professionals/c/Boulder--CO/p/'
		page = 0

		while (page < 3000):
			uri = base + str(page)
			page = page + 15

			directory_page = self.create_source_document(uri, DocType.HOUZ_DIRECTORY)
			print 'Houzz.update_directory\tget_document(%r)' % (directory_page)
			directory_page.get_document(debug=True)
			if (directory_page.doc_state == DocState.READ_WWW): self.sleep()
			if (directory_page.doc_state == DocState.READ_FAIL): self.add_error('get_document_failed', document.uri)
			self.houzz_scrape_document(directory_page)


		print 'Houzz.company listing - done'
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()




	def get_company_directory(self, update=False):
		if (self.companies is None):
			self.__read_companies_cache()
			print 'Houzz.get_company_directory(), found %d companies' % (len(self.companies))

		# if update, move and save old copy
		if (update or len(self.companies) == 0): 
			self.companies = []	# reset
			self.update_company_directory()
		return self.companies

