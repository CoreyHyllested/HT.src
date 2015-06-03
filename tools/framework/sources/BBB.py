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
	SOURCE_DATA	= 'data/sources/' + SOURCE_DIR
	SOURCE_CACHE = 'data/sources/' + SOURCE_DIR + 'cache/'


	def __init__(self, ua, queue=None):
		super(BBB, self).__init__()
		self.ua = ua
		self.directories = None
		self.doc_directories = None



	def __load_directory_of_directories(self):
		def source_document(uri):
			snap = Document(uri, doc_type=DocumentType.BBB_DIRECTORY)
			snap.location = self.SOURCE_CACHE + url_clean(uri)
			return snap

		rel_path = '/data/sources/' + self.SOURCE_DIR + '/directories.json'
		json_data	= self.read_json_file(rel_path)
		directories	= json_data.get('directories', [])
		self.directories = map(source_document, directories)



	def __read_companies_cache(self, dump_results=False):
		self.doc_companies = Document('companies.json', doc_type=DocumentType.JSON_METADATA)
		self.doc_companies.location = os.getcwd() + '/' + self.SOURCE_DATA
		self.doc_companies.filename = 'companies.json'
		self.doc_companies.read_cache(debug=True)
		self.companies = json.loads(self.doc_companies.content)
		print 'BBB.get_company_cache(), found %d companies' % (len(self.companies))
		if (dump_results): pp(companies)




	def bbb_scrape_document(self, document):
		if (document is None): return None

		if (document.doc_type == DocumentType.BBB_DIRECTORY):
			nr = self.bbb_scrape_directory(document)
			#print '\t\tscraped %s, added %d entries to companies %d' % (document.uri, nr, len(self.companies))




	def bbb_scrape_directory(self, document):
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
			self.companies.append(company)
		return len(business_dir)
	#		bbb_parse_business(bbb_uri)
	#		bbb_parse_business_reviews(name, bbb_uri)




	def update_company_directory(self):
		if (self.directories is None): self.__load_directory_of_directories()

		print 'BBB.update_company_directory() %d entries' % (len(self.directories))
		for business_directory in self.directories:
			downloaded = business_directory.save_snapshot(self.ua)
			if (downloaded): self.sleep()

			# scrape directory, add to companies
			self.bbb_scrape_document(business_directory)

		print 'BBB.Company listing - done; companies (%d)' % (len(self.companies))
		self.doc_companies.content = json.dumps(self.companies, indent=4, sort_keys=True)
		self.doc_companies.write_cache()
		



	def get_company_directory(self, update=False):
		if (self.companies is None): self.__read_companies_cache()

		if (update):
			self.companies = [] # reset
			self.update_company_directory()
		return self.companies









	def bbb_parse_business_reviews(self, name, page):
		print 'About to scrape "BBB Business Page": ' + str(page)
		page = page + '/customer-reviews'
		reviews_dom	= urllib2.urlopen(page).read()
		reviews_soup = BeautifulSoup(reviews_dom)

		pos_reviews	= reviews_soup.find(id='cr-pos-listing')
		neg_reviews	= reviews_soup.find(id='cr-neg-listing')
		neu_reviews	= reviews_soup.find(id='cr-neu-listing')

		if (pos_reviews): positive	= pos_reviews.find_all('tr')
		if (neg_reviews): negative	= neg_reviews.find_all('tr')
		if (neu_reviews): neutral	= neu_reviews.find_all('tr')

		nr_reviews	= 0
		if (positive):	nr_reviews	+= len(positive)
		if (negative):	nr_reviews	+= len(negative)
		if (neutral):	nr_reviews	+= len(neutral)

		if (not nr_reviews):
			return

		print 'There are', str(nr_reviews), 'reviews'
		fp = None
		fp = create_review(name) # pass in business name to bbb_parse_bus_page & replace 'weirdchars'
		
		for review in positive:
			r_date		= review.find(class_=['td_h']).get_text()
			r_details	= review.find(class_=['td_detail']).get_text()
			details		= r_details[0:r_details.find('This customer had a')]
			comments	= review.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
			if (fp is not None): fp.write(details)
			#print details

		for review in negative:
			r_date		= review.find(class_=['td_h']).get_text()
			r_details	= review.find(class_=['td_detail']).get_text()
			details		= r_details[0:r_details.find('This customer had a')]
			#comments	= review.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
			print details
			if (fp is not None): fp.write(details)
			
		for review in neutral:
			r_date		= review.find(class_=['td_h']).get_text()
			r_details	= review.find(class_=['td_detail']).get_text()
			details = r_details[0:r_details.find('This customer had a')]
			#comments	= review.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
			print details
			if (fp is not None): fp.write(details)
		
		if (fp is not None): fp.close()


	def bbb_parse_business(self, page):
		print 'scraping "BBB Business Page"  ' + str(page)
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
