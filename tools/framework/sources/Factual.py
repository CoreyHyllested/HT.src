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
from factual		import Factual as FactualTool
from factual.utils	import *




TOKEN='ZQZwarwcchcjD3ZTcQaQO9MJbvuzTNthvLhbmEjv'
TOKEN_SECRET='49GIM6Kw3gCCJloVFYBaQ9gSI4BCXp0tZHBRYNrU'


class Factual(Source):
	SOURCE_TYPE	= 'Factual'

	def __init__(self, queue=None):
		super(Factual, self).__init__()
		self.factual_api = FactualTool(TOKEN, TOKEN_SECRET)
		self.factual_places = self.factual_api.table('places')
		self.doc_scrapemap = { }		#intentionally
		self.directories = []


	def __load_directory_of_directories(self):
		file_path	= self.get_source_directory() + '/directories.json'
		file_json	= self.read_json_file(file_path)
		self.directories = file_json.get('directories')
		self.co_zipcodes = file_json.get('zipcodes')



	def update_company_directory(self):
		if (len(self.directories) == 0): self.__load_directory_of_directories()

		for zipcode in self.co_zipcodes:
			fact_filter	= { "region" : "CO",
							"postcode" : zipcode,
#								"$or" : [ {"locality"	: { "$eq" : "boulder" }}, {"locality"	: { "$eq" : "boulder" }} ],
												#{"locality"	: { "$eq" : "denver"  }}
									"category_ids"	: { "$includes_any" : self.directories }
			}
			print 'using zipcode', zipcode
			self.__update_company_directory_using_filter(fact_filter)



	def __update_company_directory_using_filter(self, fact_filter):
		api_places_rc	= self.factual_places.filters(fact_filter).include_count(True).limit(50)
		api_places_nr	= api_places_rc.total_row_count()
		api_collected	= self.__extract_info_from_search_results(api_places_rc)
		api_places = min(api_places_nr, 500)
		while (api_collected < api_places):
			api_places_rc	= self.factual_places.filters(fact_filter).limit(50).offset(api_collected)
			api_collected	= api_collected + self.__extract_info_from_search_results(api_places_rc)
			print 'Factual.update_company_list: %d/%d' % (api_collected, api_places)
			self.sleep(10 + random.randint(0, 15))

		print 'Factual.update_company_list -- %d / %d' % (api_collected, api_places_nr)
		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()



	def __extract_info_from_search_results(self, api_search):
		try:
			results = api_search.data()
			print '__extract %s ' % (api_search.get_url())
		except factual_api.api.APIException as e:
			print '__extract %s failed.  retry.' % (api_search.get_url())
			print type(e), e
		except Exception as e:
			print type(e), e
			
			
		for business in results:
			#pp(business)
			company = {}
			### http://www.factual.com/data/t/places/schema
			company['id_factual']	= business['factual_id']
			company['src_factual']	= 'http://factual.com/' + business['factual_id']
			company['name']			= business['name']
			company['email']		= business.get('email', None)
			company['phone']		= business.get('tel', None)
			company['website']		= business.get('website', None)
			
			self.__extract_address(business, company)
			self.__extract_hours_open(business, company)
			self.__extract_chain_info(business, company)
			self.__extract_categories(business, company)
			#pp(company)
			if (not self.co_index.get(company['src_factual'])):
				self.co_index[company['src_factual']] = company
		return len(results)

	def __extract_address(self, business, company):
		address = {}
		address['street']	= business['address']
		#address['suite']	= business['address_extended']
		address['city']		= business['locality']
		address['state']	= business['region']
		address['post']		= business['postcode']

		address['address']	= business['address']
		address['locality']	= business['locality']
		address['region']	= business['region']
		if (business.get('latitude')):		address['latitude'] =	business['latitude']
		if (business.get('longitude')):		address['longitude'] =	business['longitude']
		if (business.get('neighborhood')):	address['neighborhood'] = business.get('neighborhood')
		company['addr'] = address
#		if business.location.display_address: 	addr['display']	= business.location.display_address
#		if business.location.cross_streets:		addr['cross']	= business.location.cross_streets


	def __extract_categories(self, business, company):
		categories = business.get('category_labels', None)
		if (not categories): return
		if (len(categories) > 1):
			for x in categories:
				print x
		company['factual_categories'] = categories[0]
		

	def __extract_open_hours(self, business, company):
		pass

	def __extract_chain_info(self, business, company):
		if (business.get('chain_id') or business.get('chain_name')):
			chain_info = {}
			chain_info['chain_id']	 	= business.get('chain_id')
			chain_info['chain_name']	= business.get('chain_name')
			company['business_chain'] = chain_info
