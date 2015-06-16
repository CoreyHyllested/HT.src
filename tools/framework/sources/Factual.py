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
import factual




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
		
		cat_grp_1	= self.directories[0:13]
		cat_grp_2	= self.directories[13:]
		categories	= [cat_grp_1, cat_grp_2] # cat_grp_3, cat_grp_4]

		for zipcode in self.co_zipcodes:
			for category_list in categories:
				fact_filter	= { "region" : "CO",
								"postcode" : zipcode,
								"category_ids"	: { "$includes_any" : category_list}
				}
				self.__update_company_directory_using_filter(fact_filter, zipcode, category_list)



	def __update_company_directory_using_filter(self, fact_filter, zipcode=None, category_list=None):
		api_places_rc	= self.factual_places.filters(fact_filter).include_count(True).limit(50)
		api_places_nr	= api_places_rc.total_row_count()
		api_collected	= self.__extract_info_from_search_results(api_places_rc)
		api_places = min(api_places_nr, 500)
		print 'Factual.update_company_list: [%s|%s] %d/%d' % (zipcode, category_list, api_places, api_places_nr)
		while (api_collected < api_places):
			api_places_rc	= self.factual_places.filters(fact_filter).limit(50).offset(api_collected)
			api_collected	= api_collected + self.__extract_info_from_search_results(api_places_rc)
			self.sleep(10 + random.randint(0, 15))

		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()



	def __extract_info_from_search_results(self, api_search):
		try:
			results = api_search.data()
		except factual.api.APIException as e:
			print type(e), e
			print '__extract %s failed.  retry.' % (api_search.get_url())
			return 0
		except Exception as e:
			print type(e), e
			return 0
			
			
#		print '__extract %s ' % (api_search.get_url())
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
		if business.get('address'): 			address['street']	= business['address']
		if business.get('address_extended'):	address['suite']	= business['address_extended']
		if business.get('locality'):			address['city']		= business['locality']
		if business.get('region'):				address['state']	= business['region']
		if business.get('postcode'):			address['post']		= business['postcode']

		if business.get('address'):			address['address']	= business['address']
		if business.get('locality'):		address['locality']	= business['locality']
		if business.get('region'):			address['region']	= business['region']
		if business.get('latitude'):		address['latitude'] =	business['latitude']
		if business.get('longitude'):		address['longitude'] =	business['longitude']
		if business.get('neighborhood'):	address['neighborhood'] = business.get('neighborhood')
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
		

	def __extract_hours_open(self, business, company):
		pass

	def __extract_chain_info(self, business, company):
		if (business.get('chain_id') or business.get('chain_name')):
			chain_info = {}
			chain_info['chain_id']	 	= business.get('chain_id')
			chain_info['chain_name']	= business.get('chain_name')
			company['business_chain'] = chain_info
