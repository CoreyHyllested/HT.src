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



class Porch(Source):
	SOURCE_TYPE	= 'Porch'

	def __init__(self, queue=None):
		super(Porch, self).__init__()
		self.directories = []
		self.doc_scrapemap = self.PORCH_SCRAPEMAP


	def __load_directory_of_directories(self):
		print 'Porch.loading_directories'
		file_path	= self.get_source_directory() + '/directories.json'
		file_json	= self.read_json_file(file_path)
		self.doc_invaliddirs = file_json.get('invalid_directories')
		for directory in file_json.get('directories'):
			base = 'https://porch.com/search/results?q=%s&loc=Boulder, CO&zip=80302&lat=40.0149856&lon=-105.27054559999999&view=list&offset=%d'
			for offset in xrange(10):
				url = base % (directory, 10*offset)
				if (url in self.doc_invaliddirs): break
				directory_doc = self.create_source_document(url, DocType.PORCH_DIRECTORY)
				self.directories.append(directory_doc)


	def __scrape_business(self, document):
		print '%s.scrape_business(%s)' % (self.SOURCE_TYPE, document.location)


	def __scrape_directory(self, document):
		print '%s.scrape_business(%s)' % (self.SOURCE_TYPE, document.location)
		document_soup	= BeautifulSoup(document.content)
		business_list	= document_soup.find_all(class_=['card'])

		# WALK ALL BUSINESSES IN LIST.
		for business in business_list:
			porch_url	= self.__scrape_directory_href(business)

			company = self.co_index.get(porch_url, {})
			company['id_porch'] = business.attrs['data-company-id']
			company['src_porch'] = porch_url
			self.__scrape_directory_addr(business, company)

			porch_links = business.find_all('a')
			for link in porch_links:
				self.__scrape_directory_link(link, company)
			self.co_index[porch_url] = company
		return len(business_list)


	def __scrape_directory_href(self, business_soup):
		company_info = business_soup.find('a', class_=['pro-profile-link'])
		return company_info.attrs['href']

	def __scrape_directory_addr(self, business_soup, company):
		for span in business_soup.find_all('span', class_=['desc']):
			if (span.attrs.get('data-interaction-id') == 'search-result_company-address'):
				addr = company.get('addr', {})
				addr['full'] = span.get_text().strip()
				company['addr'] = addr

	def __scrape_directory_link(self, link, company):
		interaction = link.attrs.get('data-interaction-id')
		href = link.attrs.get('href')
		if (interaction == None):
			pass
		elif (interaction == 'search-result_company-name'):
			company['name'] = link.get_text().strip()
			company['src_' + self.source_type()] = link.attrs.get('href')
		elif (interaction == 'search-result_company-headshot'):
			headshot = link.find('div')
			if ('https://cdn.porch.com/bootstrap/headshot-professional.jpg' not in headshot.attrs['data-original']):
				company['src_headshot'] = headshot.attrs['data-original']
		elif (interaction == 'search-result_bbb-rating'):
			company['porch_bbb_rating']  = link.get_text().strip()
		elif (interaction == 'search-result_years-in-business'):
			company['porch_age'] = link.get_text().replace('in business', '').strip()
		elif (interaction == 'search-result_company-phone-link'):
			company['phone'] = re.sub('[ +()-.,]', '', link.get_text().strip())
			company['phone_display'] = link.get_text().strip()
		elif (interaction == 'search-result_company-phone-link-mobile'):
			company['phone_display'] = link.attrs['href'].replace('tel:', '').strip()
		elif (interaction == 'search-result_reviewers'):
			#print link
			div_rat	= link.find(class_=['starFill'])
			rating	= div_rat.attrs['data-stars']

			company['porch_rating'] = rating
			company['porch_reviews'] = re.sub('[()]', '', link.get_text().strip())
			company['src_porch_rating'] = link.attrs.get('href')
		elif (interaction == 'search-result_photo-projects'):
			projects = link.get_text().replace('with photos', '').strip()
			company['porch_projects'] = projects
			company['src_porch_projects'] = link.attrs.get('href')
		elif ('learn-more' in interaction):
			pass
		elif (interaction == 'search-result_nearby-projects') or (interaction == 'search-result_home-value'):
			# need to be logged in to get home-value
			# not sure what value is in the neighbors doing projects
			pass
		elif (interaction == 'search-result_company-type'):
			print link
			pass
		else:
			print href, interaction




	PORCH_SCRAPEMAP = {
		DocType.PORCH_DIRECTORY	: __scrape_directory,
		DocType.PORCH_BUSINESS	: __scrape_business
	}


	def update_company_directory(self):
		if (len(self.directories) == 0): self.__load_directory_of_directories()
		print 'Porch.update_companies, %d directories' % (len(self.directories))

		for directory in self.directories:
			directory.get_document(debug=False)
			self.scrape_document(directory)

		print 'Porch.update_companies; %d entries' % (len(self.co_index.values()))
		self.doc_companies.content = json.dumps(self.co_index.values(), indent=4, sort_keys=True)
		self.doc_companies.write_cache()
		self.companies = self.co_index.values()

