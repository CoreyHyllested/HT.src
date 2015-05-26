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

import sys, os, argparse
import urllib2, feedparser
from bs4 import BeautifulSoup, Comment
from bs4 import BeautifulSoup as Soup
import re
import yelp


CONSUMER_KEY='oLi59t3R6L2_6uQiUVgBzg'
CONSUMER_SECRET='BdeJ-Wityo8UhKPedbs8FauzWUI'
TOKEN='6UkGwKjDntk9zu-xC-LUPnFPX_RpSHib'
TOKEN_SECRET='v78DKVyg1kJGGzjWZh7HeJYLDn0'

yelp_api = yelp.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=TOKEN, access_token_secret=TOKEN_SECRET)
search_results = yelp_api.Search(category_filter='contractors', location='Boulder, CO', radius_filter='40000')
for business in search_results.businesses:
	print business.name


def create_directories():
	safe_mkdir('/data/preprocessed/reviews/')


def safe_mkdir(path):
	directory = os.getcwd() + path
	if (os.path.exists(directory) == False):
		os.makedirs(directory)



def open_file(path_from_cwd):
	filename = os.getcwd() + path_from_cwd
	print 'creating file ' + str(filename)
	fp = open(filename, 'a+')
	return fp


def create_review(filename):
	fn = '/data/preprocessed/reviews/' + filename
	fp = open_file(fn)
	fp.truncate()
	return fp


def get_bbb_types(page):
	print 'About to scrape "Business Types": ' + str(page)
	dom	= urllib2.urlopen(page).read()
	dom_soup = BeautifulSoup(dom)

	links = []
	tobs = dom_soup.find_all('ul', class_=['industry-tobs'])
	for tob in tobs:		#what is a TOB?
		LIs	= tob.find_all('a')
		for li in LIs:
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
	return types

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


		bbb_parse_address(name, addr, phone, link, img, bbb_uri)
		bbb_parse_business(bbb_uri)
		yelp_parse_business_reviews(name, bbb_uri)


def yelp_parse_business_reviews(name, page):
	print 'About to scrape "BBB Business Page": ' + str(page)



def update_yelp_businesses():
	print 'find yelp businesses'


if __name__ == '__main__':
	create_directories()

	parser = argparse.ArgumentParser(description='Collect Yelp directory of businesses; scrape, normalize, and process yelp information')
	parser.add_argument('-V', '--verbose', help="increase output verbosity", action="store_true")
	parser.add_argument('-U', '--update', help="Update business directory",	action="store_true")
	args = parser.parse_args()


	yelp_api = yelp.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=TOKEN, access_token_secret=TOKEN_SECRET)
	search_results = yelp_api.Search(category_filter='Contractors', location='Boulder, CO', limit=20, radius_filter='40000')

	if (args.verbose):
		pass
	if (args.update) or not (args.update):
		print 'Update yelp business directory!'
		businesses = update_yelp_businesses()
	search_results = yelp_api.Search(category_filter='Contractors', location='Boulder, CO', limit=20, radius_filter='40000')

