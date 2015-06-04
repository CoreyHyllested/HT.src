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
import yelp



CONSUMER_KEY='oLi59t3R6L2_6uQiUVgBzg'
CONSUMER_SECRET='BdeJ-Wityo8UhKPedbs8FauzWUI'
TOKEN='6UkGwKjDntk9zu-xC-LUPnFPX_RpSHib'
TOKEN_SECRET='v78DKVyg1kJGGzjWZh7HeJYLDn0'




class Yelp(Source):
	SOURCE_TYPE	= 'Yelp'

	def __init__(self, ua, queue=None):
		super(Yelp, self).__init__()
		self.yelp_api = yelp.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=TOKEN, access_token_secret=TOKEN_SECRET)
		self.doc_scrapemap = self.YELP_SCRAPEMAP
		self.ua = ua



	def __scrape_biz_page(self, document):
		document_soup	= BeautifulSoup(document.content)
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
			yelurl	= business.find_all(itemprop='name')[0].attrs.get('href')
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
				if (('maps.google.com' not in URI) and ('www.yelp.com' not in URI)):
					company['http'] = URI
			if (phone):		company['phone']	= phone
			if (bbburl):	company['src_bbb']	= bbburl
			if (self.companies): self.companies.append(company)
		return len(business_dir)



	YELP_SCRAPEMAP = { DocType.YELP_DIRECTORY: __scrape_biz_page }



	def update_company_directory(self):
		boulder_results = self.yelp_api.Search(category_filter='contractors', location='Boulder, CO', radius_filter='40000')
		print 'Yelp.yelp_api Boulder search() -- ', boulder_results.total

		for results_offset in range((boulder_results.total/20)+1):
			offset=results_offset * 20
			boulder_results = self.yelp_api.Search(category_filter='contractors', location='Boulder, CO', offset=offset, radius_filter='40000')

			for business in boulder_results.businesses:
				company = self.__extract_info_from_search_results(business)
				self.companies.append(company)
#			print 'Yelp.yelp_api Denver search()'
#			search_results = self.yelp_api.Search(category_filter='contractors', location='Denver, CO', radius_filter='40000')

		print 'Yelp.Company listing - done'
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()
				



	def __extract_info_from_search_results(self, business):
		company = {}
		company['name']		= business.name
		company['yelp_id']	= business.id
		business.catlist	= []

		if business.phone:		company['phone'] = business.phone
		if business.rating:		company['yelp_rating'] = business.rating
		if business.image_url:	company['src_logo'] = business.image_url
		if business.url:		company['src_yelp'] = business.url
		if business.is_closed:	company['permanently_closed']	= business.is_closed
		if business.is_claimed:	company['meta_claimed']	= business.is_claimed
		if business.review_count:	company['total_reviews'] = business.review_count
		if business.snippet_text:	company['yelp_snippet'] = business.snippet_text
		
		# simplify list ['Window Install', 'windowinstall']
		for category in business.categories:
			business.catlist.append(category[0])
		if business.catlist:	company['categories'] = business.catlist

		if business.location:
			addr = {}
			if business.location.display_address: 	addr['display']	= business.location.display_address
			if business.location.address:			addr['street']	= business.location.address
			if business.location.city:				addr['city']	= business.location.city
			if business.location.state_code:		addr['state']	= business.location.state_code
			if business.location.postal_code:		addr['post']	= business.location.postal_code
			if business.location.cross_streets:		addr['cross']	= business.location.cross_streets
			company['addr'] = addr
		return company




	def get_company_directory(self, update=False):
		if (self.companies is None): self.read_companies_cache()

		# if update, move and save old copy
		if (update): 
			self.companies = []	# reset
			self.update_company_directory()
		return self.companies

