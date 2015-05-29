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



class BBB(Source):
	SOURCE_TYPE	= 'BBB'
	SOURCE_DIR	= 'bbb/'
	SOURCE_CACHE = 'data/sources/' + SOURCE_DIR + 'cache/'
	USE_WEBCACHE = False #True
	SECONDS= 90	# get from robots.txt

	def __init__(self, queue=None):
		super(BBB, self).__init__()
		self.companies = None
		self.directories = None


	def bbb_get_directories_cache(self):
		def source_snapshot(uri):
			snap = Snapshot(uri, doc_type=DocumentType.BBB_DIRECTORY)
			snap.snap_dir = self.SOURCE_CACHE + url_clean(uri)
			return snap

		rel_path = '/data/sources/' + self.SOURCE_DIR + '/directories.json'
		json_data	= self.read_json_file(rel_path)
		directories	= json_data.get('directories', [])
		directories = map(source_snapshot, directories)
		return directories



	def bbb_get_companies_cache(self, dump_results=False):
		rel_path = '/data/sources/' + self.SOURCE_DIR + '/companies.json'
		json_data	= self.read_json_file(rel_path)
		companies = json_data.get('companies', [])
		if (dump_results): pp(companies)
		return companies



	def bbb_scrape_document(self, document):
		print '\tscraping...', document.uri
		if (document is None): return None

		if (document.doc_type == DocumentType.BBB_DIRECTORY):
			nr = self.bbb_scrape_directory(document, self.companies)





	def bbb_scrape_directory(self, snapshot, company_dir):
		document_soup	= BeautifulSoup(snapshot.document)
		business_dir	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_dir:
			addr	= business.find_all(itemtype='http://schema.org/PostalAddress')[0]
			addrStreet	= addr.find(itemprop='streetAddress').get_text()
			addrCity	= addr.find(itemprop='addressLocality').get_text()
			addrState	= addr.find(itemprop='addressRegion').get_text()

			name	= business.find_all(itemprop='name')[0].get_text()
			phone	= business.find_all(itemprop='phone')[0].get_text()
			image	= business.find_all(itemtype='http://schema.org/ImageObject')
			bbburl	= business.find_all(itemprop='name')[0].attrs.get('href')
			links	= business.find_all(class_=['link', 'newtab'])

			# create metadata
			company = {}
			company['name'] = name
			if (addr): company['addr'] = {
					"full"		: addrStreet + '\n' + addrCity + ', ' + addrState,
					"street"	: addrStreet,
					"city"		: addrCity,
					"state"		: addrState
				}
			if len(image) > 0:
				logo = image[0].attrs.get('src')
				company['src_logo'] = logo

			for uri in links:
				URI = uri.attrs.get('href')
				if (('maps.google.com' not in URI) and ('www.bbb.org' not in URI)):
					company['http'] = URI
			if (phone):		company['phone']	= phone
			if (bbburl):	company['src_bbb']	= bbburl
			if (company_dir): company_dir.append(company)
		return len(business_dir)
	#		bbb_parse_business(bbb_uri)
	#		bbb_parse_business_reviews(name, bbb_uri)




	def update_company_directory(self, ua):
		if (self.companies is None):
			#print 'update_company_directory: got company cache'
			self.companies = self.bbb_get_companies_cache()

		if (self.directories is None):
			#print 'update_company_directory: got directory cache'
			self.directories = self.bbb_get_directories_cache()

		for business_directory in self.directories:
			downloaded = business_directory.save_snapshot(ua)
			if (downloaded): time.sleep(self.SECONDS);

			# scrape directory, add to companies
			self.bbb_scrape_document(business_directory)
			#get_businesses_by_type(business_type)

		self.bbb_cache_companies()




	def bbb_cache_companies(self):
		print
		print 'Company listing'
		pp(self.companies)
		print
		print
		


	def get_company_directory(self):
		full_directory = []
		return full_directory

