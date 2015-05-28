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



class BBB(Source):
	SOURCE_DIR	= 'bbb/'
	SOURCE_CACHE = 'data/sources/' + SOURCE_DIR + '/cache'
	USE_WEBCACHE = False #True
	SECONDS= 90	# get from robots.txt

	def __init__(self):
		super(BBB, self).__init__()
		self.errors = {}
		safe_mkdir_local(self.SOURCE_CACHE)



	def bbb_top_directories(self):
		rel_path = '/data/sources/' + self.SOURCE_DIR + '/directories.json'
		json_data	= self.read_json_file(rel_path)
		directories	= json_data.get('directories', [])
		return directories


	def bbb_top_directories_testing(self):
		return  [ "http://www.bbb.org/denver/accredited-business-directory/deck-builder" ]


	def bbb_get_all_companies(self):
		rel_path = '/data/sources/' + self.SOURCE_DIR + '/companies.json'
		json_data	= self.read_json_file(rel_path)
		companies = json_data.get('companies', [])
		pp(companies)
		return companies
		

	def bbb_scrape_directory_page(self, page):
		if (self.USE_WEBCACHE):
			page = webcache_url(page)

		print 'inspect page:', page

		document = self.dl_document()
		if (document == None): return

		dom_soup = BeautifulSoup(document)
		local_businesses = dom_soup.find_all(itemtype='http://schema.org/LocalBusiness')
		print len(local_businesses), 'businesses found'
		for business in local_businesses:
			addr	= business.find_all(itemtype='http://schema.org/PostalAddress')[0]
			name	= business.find_all(itemprop='name')[0].get_text()
			phone	= business.find_all(itemprop='phone')[0].get_text()
			image	= business.find_all(itemtype='http://schema.org/ImageObject')
			links	= business.find_all(class_=['link', 'newtab'])

			bbb_uri	= business.find_all(itemprop='name')[0].attrs.get('href')

			img = None
			if len(image) > 0:
				img	= image[0].attrs.get('src')
				#print 'found logo', image

			link = None
			for uri in links:
				URI = uri.attrs.get('href')
				#print URI
				if (('maps.google.com' not in URI) and ('www.bbb.org' not in URI)):
					link = URI


	#		bbb_parse_address(name, addr, phone, link, img, bbb_uri)
	#		bbb_parse_business(bbb_uri)
	#		bbb_parse_business_reviews(name, bbb_uri)


	def update_company_directory(self):
		tl_directories = self.bbb_top_directories_testing()
		companies	= self.bbb_get_all_companies()
		for company_directory_by_type in tl_directories:
			print company_directory_by_type
			#self.bbb_scrape_directory_page(company_directory_by_type)
			#time.sleep(self.SECONDS);
			#get_businesses_by_type(business_type)

		for k, v in self.errors:
			print 'Error on ', k, v

	def get_company_directory(self):
		full_directory = []
		return full_directory

