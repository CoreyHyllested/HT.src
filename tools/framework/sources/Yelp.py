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
	SOURCE_DIR	= 'yelp/'
	SOURCE_DATA	= 'data/sources/' + SOURCE_DIR
	SOURCE_CACHE = 'data/sources/' + SOURCE_DIR + 'cache/'
	USE_WEBCACHE = False
	SECONDS = 90	# get from robots.txt

	def __init__(self, ua, queue=None):
		super(Yelp, self).__init__()
		self.yelp_api = yelp.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=TOKEN, access_token_secret=TOKEN_SECRET)
		self.ua = ua
		self.companies = None
		self.doc_companies = None



	def __read_companies_cache(self, dump_results=False):
		self.doc_companies = Document('companies.json', doc_type=DocumentType.JSON_METADATA)
		self.doc_companies.location = os.getcwd() + '/' + self.SOURCE_DATA
		self.doc_companies.filename = 'companies.json'
		self.doc_companies.read_cache(debug=True)
		companies = json.loads(self.doc_companies.content)
		if (dump_results): pp(companies)
		return companies




	def yelp_scrape_document(self, document):
		if (document is None): return None

		if (document.doc_type == DocumentType.YELP_DIRECTORY):
			nr = self.yelp_scrape_directory(document)
			print '\t\tscraped %s, added %d entries' % (document.uri, nr)




	def yelp_scrape_directory(self, document):
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
		if (self.companies is None):
			self.companies = self.__read_companies_cache()
			print 'Yelp.get_company_directory(), found %d companies' % (len(self.companies))

		# if update, move and save old copy
		if (update): 
			self.companies = []	# reset
			self.update_company_directory()
		return self.companies







	def yelp_parse_business(self, page):
		print 'scraping "YELP Business Page"  ' + str(page)
		dom	= urllib2.urlopen(page).read()
		dom_soup = BeautifulSoup(dom)

		#print 'Finding LocalBusiness'
		business = dom_soup.find_all(itemtype='http://schema.org/LocalBusiness')[0]

		#print 'Get name, telephone, address'
		bus_name	= business.find_all(itemprop='name')[0].get_text()
		bus_phone	= business.find_all(itemprop='telephone')[0].get_text()
		bus_address	= business.find_all(itemtype='http://schema.org/PostalAddress')[0]
		bus_addr_street	= bus_address.find_all(itemprop='streetAddress')[0].get_text()
		bus_addr_locale	= bus_address.find_all(itemprop='addressLocality')[0].get_text()
		bus_addr_region	= bus_address.find_all(itemprop='addressRegion')[0].get_text()
		bus_addr_postal = bus_address.find_all(itemprop='postalCode')[0].get_text()
		print bus_name, bus_phone, bus_addr_street, bus_addr_locale, bus_addr_region, bus_addr_postal

#	bus_contact_url	= business.find_all(class_='business-link')[0].get_text()

		#print 'Get accredited information'
		rating = None
		accredited_since	= business.find_all(class_='accredited-since')[0].get_text()
		accredited_rating	= business.find_all(id='accedited-rating')	#BBB misspells this, check to see if it got fixed, not always present.
		if (accredited_rating):
			rating = accredited_rating[0].img.attrs.get('title')
		print accredited_since, rating
		#TODO look for <span class='business-email'><a href=mailto:>
		#TODO also look for addtional email addresses; parse mailto?  <div id='addtional-email-pop'><li><a href=mailto?>

		
		#print 'Get additional business information'
		bus_additional = business.find(id='business-additional-info-container')
		bus_bbb_open = bus_additional.find('span').get_text()
		bus_founding	= bus_additional.find(itemprop='foundingDate').get_text()	#also just business.search

		bus_info_legal = bus_additional.find('h5', text='Type of Entity')
		if bus_info_legal is not None:
			bus_info_legal = bus_info_legal.nextSibling.get_text()

		print 'Business Opened:  ' + str(bus_bbb_open)
		print 'Business Founded: ' + str(bus_founding)
		print 'Business Legal Status: ' + str(bus_info_legal)

		#print 'Get employee information'
		bus_info_employees = bus_additional.find(itemprop='employees')
		if bus_info_employees == None:
			bus_emp = bus_additional.find('h5', text='Business Management').nextSibling.get_text()
			print bus_emp
			bus_info_employees = []
		for emp in bus_info_employees:
			#print 'Job title?: ', emp.get_text()
			emp_name = emp.find(itemprop='name')
			if (emp_name is not None): emp_name = emp_name.get_text()
			emp_title = emp.find(itemprop='jobTitle')
			if (emp_title is not None): emp_title = emp_title.get_text()
			#print 'person name:', emp_name
			#print 'person job:', emp_title


		#print 'Get category information'
		bus_info_categories	= bus_additional.find('h5', text='Business Category').nextSibling.get_text().split(',')
		print bus_info_categories
		
		print 'Get additional names'
		bus_alt_names = bus_additional.find('h5', text='Alternate Business Names')
		if bus_alt_names is not None: 
			bus_alt_names = bus_alt_names.nextSibling.get_text().split(',')
		print bus_alt_names


		print 'Get rating information'
		bus_agg_rating = bus_additional.find(itemtype='http://schema.org/AggregateRating')
		print 'bus_agg_rating:', bus_agg_rating
		if bus_agg_rating is not None:
			bus_agg_score	= bus_agg_rating.find(itemprop='ratingValue')
			if (bus_agg_score): bus_agg_score = bus_agg_score.attrs.get('content')
			bus_agg_best	= bus_agg_rating.find(itemprop='bestRating')
			if (bus_agg_best): bus_agg_best = bus_agg_best.attrs.get('content')
			bus_agg_count	= bus_agg_rating.find(itemprop='reviewCount')
			if (bus_agg_count): bus_agg_count = bus_agg_count.attrs.get('content')

			print bus_agg_count, 'reviews, with an avg score of', bus_agg_score
			print 'Best score', bus_agg_best
