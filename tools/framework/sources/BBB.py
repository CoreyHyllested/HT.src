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

	def __init__(self, queue=None):
		super(BBB, self).__init__()
		self.directories = []
		self.doc_scrapemap = self.BBB_SCRAPEMAP


	def __load_directory_of_directories(self):
		file_path = self.get_source_directory() + '/directories.json'
		directories = self.read_json_file(file_path)
		for directory in directories:
			document = self.create_source_document(directory, DocType.BBB_DIRECTORY)
			self.directories.append(document)


	def __scrape_directory(self, document):
		document_soup	= BeautifulSoup(document.content)
		business_dir	= document_soup.find_all(itemtype='http://schema.org/LocalBusiness')

		# WALK ALL BUSINESSES IN DIR.
		for business in business_dir:
			httpid	= self.__scrape_directory_href(business)
			company = self.co_index.get(httpid, {})

			company['src_bbb']	= httpid
			company['id_bbb']	= httpid
			company['name']		= business.find(itemprop='name').get_text()
			self.__scrape_directory_addr(business,	company)
			self.__scrape_directory_http(business,	company)
			self.__scrape_directory_logo(business,	company)
			self.__scrape_directory_phone(business,	company)
			self.co_index[httpid] = company
		return len(business_dir)



	def __scrape_directory_href(self, bus_soup):
		return bus_soup.find(itemprop='name').attrs['href']


	def __scrape_directory_addr(self, business_soup, company):
		addr_soup = business_soup.find(itemtype='http://schema.org/PostalAddress')
		if (not addr_soup): return

		addrStreet	= addr_soup.find(itemprop='streetAddress')
		addrCity	= addr_soup.find(itemprop='addressLocality')
		addrState	= addr_soup.find(itemprop='addressRegion')
		addrPostal	= addr_soup.find(itemprop='postalCode')

		addr = company.get('addr', {})
		if (addrStreet):	addr['street'] = addrStreet.get_text()
		if (addrCity):		addr['city'] = addrCity.get_text()
		if (addrState):		addr['state'] = addrState.get_text()
		if (addrPostal):	addr['post'] = addrPostal.get_text()
		company['addr'] = addr


	def __scrape_directory_http(self, bus_soup, company):
		links = bus_soup.find_all(class_=['link', 'newtab'])
		for uri in links:
			URI = uri.attrs.get('href')
			if (('maps.google.com' not in URI) and ('www.bbb.org' not in URI)):
				company['business_www'] = URI


	def __scrape_directory_logo(self, bus_soup, company):
		image = bus_soup.find(itemtype='http://schema.org/ImageObject')
		if (image): company['src_logo'] = image.attrs.get('src')


	def __scrape_directory_phone(self, bus_soup, company):
		phone	= bus_soup.find(itemprop='phone').get_text()
		if (phone): 
			company['phone_display'] = phone
			company['phone'] = re.sub('[ +()-.,]', '', phone)


	def update_company_directory(self):
		if (len(self.directories) == 0): self.__load_directory_of_directories()
		print '%s.update_companies, %d directories' % (self.SOURCE_TYPE, len(self.directories))

		for business_directory in self.directories:
			business_directory.get_document(debug=False)
			self.scrape_document(business_directory)

		print '%s.update_companies; %d entries' % (self.SOURCE_TYPE, len(self.co_index.values()))
		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()
		self.companies = self.co_index.values()



	def __scrape_reviews(self, name, page):
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



	def __scrape_business(self, page):
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

	BBB_SCRAPEMAP = {
		DocType.BBB_DIRECTORY	: __scrape_directory,
		DocType.BBB_REVIEW		: __scrape_reviews,
		DocType.BBB_BUSINESS	: __scrape_business
	}

