''' BBB-Scrape '''

import urllib2
from bs4 import BeautifulSoup, Comment
from bs4 import BeautifulSoup as Soup
from soupselect import select
import feedparser
import re



def get_bbb_types(page):
	print 'About to scrape "Business Types": ' + str(page)
	dom	= urllib2.urlopen(page).read()
	dom_soup = BeautifulSoup(dom)

	links = []
	tobs = dom_soup.find_all('ul', class_=['industry-tobs'])
	for tob in tobs:
#		print '\tTOB', tob
		LIs	= tob.find_all('a')
		for li in LIs:
#			print '\t\tTOB-LI', li
			uri	= li.attrs.get('href')
			print '\"' + str(uri) + '\",'
			links.append(uri)
	return links

def get_bbb_types_cached():
	types = [	"http://www.bbb.org/denver/accredited-business-directory/air-conditioning-and-heating-contractors-residential",
				"http://www.bbb.org/denver/accredited-business-directory/asphalt",
				"http://www.bbb.org/denver/accredited-business-directory/backflow-prevention-devices-and-services",
				"http://www.bbb.org/denver/accredited-business-directory/basement-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/basement-finishing",
				"http://www.bbb.org/denver/accredited-business-directory/basement-remodeling",
				"http://www.bbb.org/denver/accredited-business-directory/bathroom-remodeling",
				"http://www.bbb.org/denver/accredited-business-directory/blinds",
				"http://www.bbb.org/denver/accredited-business-directory/building-construction-consultants",
				"http://www.bbb.org/denver/accredited-business-directory/building-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/building-inspection",
				"http://www.bbb.org/denver/accredited-business-directory/building-materials",
				"http://www.bbb.org/denver/accredited-business-directory/building-restoration-and-preservation",
				"http://www.bbb.org/denver/accredited-business-directory/buildings-pre-cut-prefab-and-modular-dealers",
				"http://www.bbb.org/denver/accredited-business-directory/cabinet-refacing",
				"http://www.bbb.org/denver/accredited-business-directory/cabinets",
				"http://www.bbb.org/denver/accredited-business-directory/carpenters",
				"http://www.bbb.org/denver/accredited-business-directory/carpet-and-rug-cleaners",
				"http://www.bbb.org/denver/accredited-business-directory/ceiling-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/chain-link-fence-sales-service-and-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-custom",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-stamped-and-decorative",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-blocks-and-shapes",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-removal",
				"http://www.bbb.org/denver/accredited-business-directory/concrete-repair-leveling",
				"http://www.bbb.org/denver/accredited-business-directory/construction-and-remodeling-services",
				"http://www.bbb.org/denver/accredited-business-directory/construction-equipment-sales-services",
				"http://www.bbb.org/denver/accredited-business-directory/construction-management",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-decorative-and-specialty-concrete",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-electrical",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-flat-roof",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-general-green-builder",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-interior-trim",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-remodel-and-repair",
				"http://www.bbb.org/denver/accredited-business-directory/contractor-tile-roofing",
				"http://www.bbb.org/denver/accredited-business-directory/contractors-framing",
				"http://www.bbb.org/denver/accredited-business-directory/contractors-gutters",
				"http://www.bbb.org/denver/accredited-business-directory/contractors-solar-energy",
				"http://www.bbb.org/denver/accredited-business-directory/contractors-equipment-and-supplies-rent-and-lease",
				"http://www.bbb.org/denver/accredited-business-directory/contractors-general",
				"http://www.bbb.org/denver/accredited-business-directory/counter-tops",
				"http://www.bbb.org/denver/accredited-business-directory/deck-builder",
				"http://www.bbb.org/denver/accredited-business-directory/doors",
				"http://www.bbb.org/denver/accredited-business-directory/drywall-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/elevator-installation",
				"http://www.bbb.org/denver/accredited-business-directory/energy-conservation-products-and-services",
				"http://www.bbb.org/denver/accredited-business-directory/engineers-structural",
				"http://www.bbb.org/denver/accredited-business-directory/erosion-control",
				"http://www.bbb.org/denver/accredited-business-directory/excavating-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/fence-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/fire-and-water-damage-restoration",
				"http://www.bbb.org/denver/accredited-business-directory/floor-laying-refinishing-and-resurfacing",
				"http://www.bbb.org/denver/accredited-business-directory/foundation-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/foundation-repair-and-house-leveling",
				"http://www.bbb.org/denver/accredited-business-directory/fumigation-services",
				"http://www.bbb.org/denver/accredited-business-directory/garage-builders",
				"http://www.bbb.org/denver/accredited-business-directory/granite",
				"http://www.bbb.org/denver/accredited-business-directory/grout-resurfacing-and-repair",
				"http://www.bbb.org/denver/accredited-business-directory/gutters-and-downspouts",
				"http://www.bbb.org/denver/accredited-business-directory/handyman-services",
				"http://www.bbb.org/denver/accredited-business-directory/heating-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/home-builders",
				"http://www.bbb.org/denver/accredited-business-directory/home-improvements",
				"http://www.bbb.org/denver/accredited-business-directory/home-inspection-service",
				"http://www.bbb.org/denver/accredited-business-directory/insulation-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/kitchen-and-bath-design-and-remodeling",
				"http://www.bbb.org/denver/accredited-business-directory/kitchen-remodeling",
				"http://www.bbb.org/denver/accredited-business-directory/landscape-architects",
				"http://www.bbb.org/denver/accredited-business-directory/landscape-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/landscape-designers",
				"http://www.bbb.org/denver/accredited-business-directory/landscaping-clean-up-spring-and-fall",
				"http://www.bbb.org/denver/accredited-business-directory/lawn-and-garden-sprinkler-systems",
				"http://www.bbb.org/denver/accredited-business-directory/marble-and-granite-installation-stonework-fabrication",
				"http://www.bbb.org/denver/accredited-business-directory/mason-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/mechanical-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/modular-homes",
				"http://www.bbb.org/denver/accredited-business-directory/mold-and-mildew-inspection",
				"http://www.bbb.org/denver/accredited-business-directory/mud-jacking-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/painting-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/patio-and-deck-builders",
				"http://www.bbb.org/denver/accredited-business-directory/patio-builder",
				"http://www.bbb.org/denver/accredited-business-directory/patio-doors",
				"http://www.bbb.org/denver/accredited-business-directory/patio-porch-and-deck-enclosures",
				"http://www.bbb.org/denver/accredited-business-directory/paving-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/paving-materials",
				"http://www.bbb.org/denver/accredited-business-directory/pipe-bending-and-fabricating",
				"http://www.bbb.org/denver/accredited-business-directory/plumbing-plan-services",
				"http://www.bbb.org/denver/accredited-business-directory/radon-mitigation",
				"http://www.bbb.org/denver/accredited-business-directory/referral-contractor",
				"http://www.bbb.org/denver/accredited-business-directory/remodeling-services",
				"http://www.bbb.org/denver/accredited-business-directory/retaining-walls",
				"http://www.bbb.org/denver/accredited-business-directory/roofing-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/roofing-materials",
				"http://www.bbb.org/denver/accredited-business-directory/roofing-service-consultants",
				"http://www.bbb.org/denver/accredited-business-directory/rubbish-and-garbage-removal",
				"http://www.bbb.org/denver/accredited-business-directory/security-control-equipment-and-system-monitors",
				"http://www.bbb.org/denver/accredited-business-directory/sewer-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/sewer-inspection",
				"http://www.bbb.org/denver/accredited-business-directory/siding-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/solar-energy-equipment-and-systems-dealers",
				"http://www.bbb.org/denver/accredited-business-directory/solar-energy-products-service-and-repair",
				"http://www.bbb.org/denver/accredited-business-directory/solar-energy-system-design-and-installation",
				"http://www.bbb.org/denver/accredited-business-directory/steel-fabricators",
				"http://www.bbb.org/denver/accredited-business-directory/stone-setting-interlocking-pavers",
				"http://www.bbb.org/denver/accredited-business-directory/sunroom-and-solarium-design-and-construction",
				"http://www.bbb.org/denver/accredited-business-directory/swimming-pool-contractors-dealers-design",
				"http://www.bbb.org/denver/accredited-business-directory/tile-restoration",
				"http://www.bbb.org/denver/accredited-business-directory/vinyl-flooring",
				"http://www.bbb.org/denver/accredited-business-directory/water-damage-restoration",
				"http://www.bbb.org/denver/accredited-business-directory/water-main-contractors",
				"http://www.bbb.org/denver/accredited-business-directory/windows"
	]
	#return types
	testing = [	"http://www.bbb.org/denver/accredited-business-directory/deck-builder" ]
	return testing


def bbb_parse_address(name, addr, phone, link, image=None, bbb_uri=None):
	addrStreet	= addr.find(itemprop='streetAddress').get_text()
	addrCity	= addr.find(itemprop='addressLocality').get_text()
	addrState	= addr.find(itemprop='addressRegion').get_text()

	print
	print name, phone
	print link
	print addrStreet
	print str(addrCity) + ', ' + str(addrState)
	print 'Logo:', image
	print 'BBB:  ', bbb_uri
	print
	print
	print


def get_businesses_by_type(page):
	print 'About to scrape "Businesses by Type": ' + str(page)
	dom	= urllib2.urlopen(page).read()
	dom_soup = BeautifulSoup(dom)

	#local_businesses = dom_soup.find_all(id=re.compile('list[0-9]+'))
	local_businesses = dom_soup.find_all(itemtype='http://schema.org/LocalBusiness')
	print len(local_businesses), 'businesses found'
	for business in local_businesses:
		#sponsor = business.find_all(class_=['sponsorBx'])
		addr	= business.find_all(itemtype='http://schema.org/PostalAddress')[0]
		name	= business.find_all(itemprop='name')[0].get_text()
		phone	= business.find_all(itemprop='phone')[0].get_text()
		image	= business.find_all(itemtype='http://schema.org/ImageObject')
		links	= business.find_all(class_=['link', 'newtab'])

		bbb_uri	= business.find_all(itemprop='name')[0].attrs.get('href')

		if len(image) > 0:
			image	= image[0].attrs.get('src')
			#print 'found logo', image
		else:
			image = None


		for uri in links:
			URI = uri.attrs.get('href')
			print URI
			if (('maps.google.com' not in URI) and ('www.bbb.org' not in URI)):
				link = URI


		bbb_parse_address(name, addr, phone, link, image, bbb_uri)
		bbb_parse_business(bbb_uri)
		bbb_parse_business_reviews(bbb_uri)


def bbb_parse_business_reviews(page):
	print 'About to scrape "BBB Business Page": ' + str(page)
	page = page + '/customer-reviews'
	reviews_dom	= urllib2.urlopen(page).read()
	reviews_soup = BeautifulSoup(reviews_dom)
	positive = reviews_soup.find(id='cr-pos-listing')
	reviews	= positive.find_all('tr')
	for r in reviews:
		r_date		= r.find(class_=['td_h']).get_text()
		r_details	= r.find(class_=['td_detail']).get_text()
		comments	= r.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
		print r_date
		details = r_details[0:r_details.find('This customer had a')]
		print details

	negative = reviews_soup.find(id='cr-neg-listing')
	reviews	= negative.find_all('tr')
	for r in reviews:
		r_date		= r.find(class_=['td_h']).get_text()
		r_details	= r.find(class_=['td_detail']).get_text()
		#comments	= r.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
		print r_date
		details = r_details[0:r_details.find('This customer had a')]
		print details
		
	neutral	 = reviews_soup.find(id='cr-neu-listing')
	reviews	= neutral.find_all('tr')
	for r in reviews:
		r_date		= r.find(class_=['td_h']).get_text()
		r_details	= r.find(class_=['td_detail']).get_text()
		#comments	= r.findAll(text=lambda text:isinstance(text, Comment))	#has email address, use the get project price by pulling permits?
		print r_date
		details = r_details[0:r_details.find('This customer had a')]
		print details
	


def bbb_parse_business(page):
	print 'About to scrape "BBB Business Page": ' + str(page)
	dom	= urllib2.urlopen(page).read()
	dom_soup = BeautifulSoup(dom)

	print 'Finding LocalBusiness'
	business = dom_soup.find_all(itemtype='http://schema.org/LocalBusiness')[0]

	print 'Get name, telephone, address'
	bus_name	= business.find_all(itemprop='name')[0].get_text()
	bus_phone	= business.find_all(itemprop='telephone')[0].get_text()
	bus_address	= business.find_all(itemtype='http://schema.org/PostalAddress')[0]
	bus_addr_street	= bus_address.find_all(itemprop='streetAddress')[0].get_text()
	bus_addr_locale	= bus_address.find_all(itemprop='addressLocality')[0].get_text()
	bus_addr_region	= bus_address.find_all(itemprop='addressRegion')[0].get_text()
	bus_addr_postal = bus_address.find_all(itemprop='postalCode')[0].get_text()
	print bus_name, bus_phone, bus_addr_street, bus_addr_locale, bus_addr_region, bus_addr_postal

#	bus_contact_url	= business.find_all(class_='business-link')[0].get_text()

	print 'Get accredited information'
	accredited_since	= business.find_all(class_='accredited-since')[0].get_text()
	accredited_rating	= business.find_all(id='accedited-rating')	#BBB misspells this, check to see if it got fixed
#	print accredited_since, accredited_rating
	rating = accredited_rating[0].img.attrs.get('title')
	print accredited_since, rating
	
	print 'Get additional business information'
	bus_additional = business.find(id='business-additional-info-container')
	bus_bbb_open = bus_additional.find('span').get_text()
	bus_founding	= bus_additional.find(itemprop='foundingDate').get_text()	#also just business.search

	bus_info_legal = bus_additional.find('h5', text='Type of Entity')
	if bus_info_legal is not None:
		bus_info_legal = bus_info_legal.nextSibling.get_text()

	print bus_bbb_open
	print bus_founding
	print bus_info_legal

	print 'Get employee information'
	bus_info_employees = bus_additional.find(itemprop='employees')
	if bus_info_employees == None:
		bus_emp = bus_additional.find('h5', text='Business Management').nextSibling.get_text()
		print bus_emp
		bus_info_employees = []
	for emp in bus_info_employees:
		print 'Job title?: ', emp.get_text()
		emp_name = emp.find(itemprop='name')
		if (emp_name is not None): emp_name = emp_name.get_text()
		emp_title = emp.find(itemprop='jobTitle')
		if (emp_title is not None): emp_title = emp_title.get_text()
		print 'person name:', emp_name
		print 'person job:', emp_title


	print 'Get category information'
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


if __name__ == '__main__':
	print 'Scrape BBB'
#	types = get_bbb_types('http://www.bbb.org/denver/accredited-business-directory/contractors-construction-and-building-materials-industry')
	types = get_bbb_types_cached()
	for business_type in types:
		get_businesses_by_type(business_type)
#	bbb_parse_business('http://www.bbb.org/denver/business-reviews/roofing-contractors/303-933-roof-in-littleton-co-75003621')
#	bbb_parse_business_reviews('http://www.bbb.org/denver/business-reviews/roofing-contractors/303-933-roof-in-littleton-co-75003621')
		



