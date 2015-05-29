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
from models import Snapshot
from controllers import *



class BBB(Source):
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
			snap = Snapshot(uri)
			snap.snap_dir = self.SOURCE_CACHE + url_clean(uri)
			return snap

		rel_path = '/data/sources/' + self.SOURCE_DIR + '/directories.json'
		json_data	= self.read_json_file(rel_path)
		directories	= json_data.get('directories', [])
		directories = map(source_snapshot, directories)
		return directories


	def bbb_get_directories_cache_testing(self):
		return  [ Snapshot("http://www.bbb.org/denver/accredited-business-directory/deck-builder") ]


	def bbb_get_companies_cache(self):
		rel_path = '/data/sources/' + self.SOURCE_DIR + '/companies.json'
		json_data	= self.read_json_file(rel_path)
		companies = json_data.get('companies', [])
		pp(companies)
		return companies
		

	def bbb_scrape_directory(self, dir_page, company_dir):
		if (dir_page.document is None):
			print dir_page, 'is none'
			return

		dom_soup = BeautifulSoup(dir_page.document)
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

			self.bbb_parse_address(name, addr, phone, link, company_dir, img, bbb_uri)
	#		bbb_parse_business(bbb_uri)
	#		bbb_parse_business_reviews(name, bbb_uri)



	def bbb_parse_address(self, name, addr, phone, link, company_dir, image=None, bbb_uri=None):
		company = {}
		addrStreet	= addr.find(itemprop='streetAddress').get_text()
		addrCity	= addr.find(itemprop='addressLocality').get_text()
		addrState	= addr.find(itemprop='addressRegion').get_text()

		company['name'] = name
		if (addr):	company['addr'] = {
			"full"		: addrStreet + '\n' + addrCity + ', ' + addrState,
			"street"	: addrStreet,
			"city"		: addrCity,
			"state"		: addrState
		}
		if (link):	company['link'] = link
		if (phone):	company['phone'] = phone
		if (image):	company['image'] = image
		if (bbb_uri):	company['bbb_uri'] = bbb_uri
#		pp(company_dir)
#		print '=COMPANY========================='
#		pp(company)
#		print '================================='
		company_dir.append(company)

		#print
		#print name, phone
		#print link
		#print addrStreet
		#print str(addrCity) + ', ' + str(addrState)
		#print 'Logo:', image
		#print 'BBB:  ', bbb_uri
		#print
		#print


	def update_company_directory(self, ua):
		if (self.companies is None):
			print 'update_company_directory: got company cache'
			self.companies = self.bbb_get_companies_cache()

		if (self.directories is None):
			print 'update_company_directory: got directory cache'
			self.directories = self.bbb_get_directories_cache()

		for business_directory in self.directories:
			saved = business_directory.save_snapshot(ua)
			if (not saved):
				print business_directory, 'prev. saved, continue'
				continue

			print 'saved', business_directory, 'now sleeping'
			self.bbb_scrape_directory(business_directory, self.companies)
			time.sleep(self.SECONDS);
			#get_businesses_by_type(business_type)

		#for k, v in self.errors:
		#	print 'Error on ', k, v


	def get_company_directory(self):
		full_directory = []
		return full_directory

