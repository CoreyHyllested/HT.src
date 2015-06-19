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
		self.doc_scrapemap = {}		#intentionally empty
		self.directories = []


	def __load_directory_of_directories(self):
		file_path	= self.get_source_directory() + '/directories.json'
		file_json	= self.read_json_file(file_path)
		self.directories = file_json.get('directories')
		self.co_zipcodes = file_json.get('zipcodes')



	def update_company_directory(self):
		if (len(self.directories) == 0): self.__load_directory_of_directories()
		
		for zipcode in self.co_zipcodes:
			categories = [ self.directories ]
			if ('-sp' in zipcode):
				zipcode		= zipcode.strip('-sp')
				categories	= [ self.directories[0:13], self.directories[13:] ]

			for category_list in categories:
				fact_filter	= { "region" : "CO",
								"postcode" : zipcode,
								"category_ids"	: { "$includes_any" : category_list}
				}
				try:
					self.__update_company_directory_using_filter(fact_filter, zipcode, category_list)
				except factual.api.APIException as e:
					print type(e), e
					print '__update_company_dir failed.'

		# CAH-move back here.
			print '%s.update_companies; writing %d entries' % (self.SOURCE_TYPE, len(self.co_index.values()))
			self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
			self.doc_companies.write_cache()



	def __update_company_directory_using_filter(self, fact_filter, zipcode=None, category_list=None):
		api_places_rc	= self.factual_places.filters(fact_filter).include_count(True).limit(50)
		api_places_nr	= api_places_rc.total_row_count()
		api_collected	= self.__extract_info_from_search_results(api_places_rc, zipcode, 0)
		api_places = min(api_places_nr, 500)
		print 'Factual.update_company_list: [%s] %d/%d' % (zipcode, api_places, api_places_nr)
		while (api_collected < api_places):
			api_places_rc	= self.factual_places.filters(fact_filter).limit(50).offset(api_collected)
			api_collected	= api_collected + self.__extract_info_from_search_results(api_places_rc, zipcode, api_collected)
			self.sleep(10 + random.randint(0, 15))

		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()



	def __extract_info_from_search_results(self, api_search, zipcode, collected):
		try:
			results = api_search.data()
		except factual.api.APIException as e:
			print type(e),'api_search.data() failed.'
			print 'zip %d, offset %d' % (zipcode, collected)
			print 'retry.' % (api_search.get_url())
			return 0
		except Exception as e:
			print type(e), e
			return 0


		for business in results:
			company = {}
			source	= []
			### http://www.factual.com/data/t/places/schema
			company['_id_factual']	= business['factual_id']
			company['business_name']	= business['name']
			source =	{
							'factual' : {
								'id'	: business['factual_id'],
								'src'	: 'http://factual.com/' + business['factual_id']
							}
						}
			company['source'] = [].append(source)

			self.__extract_address(business, company)
			self.__extract_contact(business, company)
			self.__extract_categories(business, company)
			self.__extract_chain_info(business, company)
			self.__extract_hours_info(business, company)

			#if (not self.co_index.get(company['_id_factual'])):
			self.co_index[company['_id_factual']] = company
		return len(results)



	def __extract_address(self, business, company):
		address = {}
		meta = {}

		meta['lat'] = business.get('latitude',	None)
		meta['lng'] = business.get('longitude',	None)
		meta['neighborhood'] = business.get('neighborhood', None)

		# done alphabetically, for your own ease of reading.
		address['city']		= business.get('locality',	None)
		address['meta']		= meta
		address['state']	= business.get('region',	None)
		address['street']	= business.get('address',	None)
		address['suite']	= business.get('address_extended', None)
		address['post']		= business.get('postcode',	None)

		company['address'] = address


	def __extract_contact(self, business, company):
			self.normalize_email(business.get('email'), company)
			self.normalize_phone(business.get('tel'), company)
			self.normalize_website(business.get('website'), company)


	def __extract_categories(self, business, company):
		categories = business.get('category_labels', None)
		if (not categories): return
		if (len(categories) > 1):
			for x in categories:
				print x
		company['categories'] = [ { 'factual' : categories[0] } ]
		

	def __extract_hours_info(self, business, company):
		if business.get('hours_display'):
			company['hours'] = [ { 'factual' : business.get('hours_display') } ]


	def __extract_chain_info(self, business, company):
		if (business.get('chain_id') or business.get('chain_name')):
			chain_info = {}
			chain_info['chain_id']	 	= business.get('chain_id')
			chain_info['chain_name']	= business.get('chain_name')
			company['business_chain'] = chain_info

