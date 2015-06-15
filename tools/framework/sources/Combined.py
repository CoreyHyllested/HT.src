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
import urltools



class Combine(object):
	companies	= []
	idx_phone	= {}
	idx_name	= {}
	idx_site	= {}

	matched		= {}
	matched['phone_name']	= 0
	matched['phone_site']	= 0
	matched['site_name']	= 0

	matched['bbb']			= { 'bbb' : 0, 'homeadvisor' : 0, 'houzz' : 0, 'porch' : 0, 'yelp' : 0 }
	matched['homeadvisor']	= { 'bbb' : 0, 'homeadvisor' : 0, 'houzz' : 0, 'porch' : 0, 'yelp' : 0 }
	matched['houzz']		= { 'bbb' : 0, 'homeadvisor' : 0, 'houzz' : 0, 'porch' : 0, 'yelp' : 0 }
	matched['porch']		= { 'bbb' : 0, 'homeadvisor' : 0, 'houzz' : 0, 'porch' : 0, 'yelp' : 0 }
	matched['yelp']			= { 'bbb' : 0, 'homeadvisor' : 0, 'houzz' : 0, 'porch' : 0, 'yelp' : 0 }

	def __init__(self):
		super(Combine, self).__init__()


	@staticmethod
	def add_source(source):
		directory = source.get_company_directory()
		source_id = 'src_' + source.source_type()
		
		print 'Combine.adding %s.index(%d)' % (source.source_type(), len(directory))
		for company in directory:
			b = Business(company, source.source_type())
			m_phone = Combine.idx_phone.get(b.business_phone)
			m_name	= Combine.idx_name.get(b.name)
			m_site	= Combine.idx_site.get(b.business_www)
			
			if (not m_phone) and (not m_name) and (not m_site):
				# implies a new business
				Combine.companies.append(b)
				if (b.name):			Combine.idx_name[b.name] = b
				if (b.business_phone):	Combine.idx_phone[b.business_phone] = b
				if (b.business_www):	Combine.idx_site[b.business_www] = b
				#print 'Adding', b.business_id, b.name
				continue
			
			if (m_site and m_phone and m_name): 
				print 'ANY TAKERS?'

			if (m_site and m_phone):
				if (m_site != m_phone): raise Exception('phone != site', m_phone, m_site, b)

				m_phone.merge(b, 'phone_site')
				Combine.matched['phone_site'] = Combine.matched['phone_site'] + 1
				Combine.matched[m_phone.source][b.source] = Combine.matched[m_phone.source][b.source] + 1
				continue

			if (m_site and m_name):
				if (m_name != m_site): raise Exception('phone != site', m_name, m_site, b)

#				m_name.merge(b, 'name_site')
				Combine.matched['name_site'] = Combine.matched['name_site'] + 1
				Combine.matched[m_phone.source][b.source] = Combine.matched[m_phone.source][b.source] + 1
				continue


			if (m_phone and m_name):
				if (m_phone != m_name):	
					print '===================================================='
					print 'QUA? phone != name', b.phone, b.name
					print 'matched phone:', m_phone.phone, m_phone.name, distance(m_phone.name, b.name)
					print 'matched name:',  m_name.phone, m_name.name
					print '-addr-----------------------------------------------'
					pp(b.addr)
					pp(m_phone.addr)
					pp(m_name.addr)
					#print m_phone.addr.street
					#print m_name.addr.street
					print '----------------------------------------------------'
					print '====================================================\n'

				if (m_phone == m_name):
#					m_phone.merge(b, 'phone_name')
					Combine.matched['phone_name'] = Combine.matched['phone_name'] + 1
					Combine.matched[m_phone.source][b.source] = Combine.matched[m_phone.source][b.source] + 1
					continue



#			if (m_site):
#				m_site.merge(b, 'website')

			if (m_phone):
				# does not match name or site.
#				m_phone.merge(b, 'just phone')
				pass
				
			#print b.business_id, b.name
			

			#Combine.companies[business.get(source_id)] = business

		print 'Combine.companies sz[%d]' % (len(Combine.companies))
		print 'Combine.phone_idx sz[%d]' % (len(Combine.idx_phone))


	@staticmethod
	def save_output():
		#merge_auto	= path_from_cwd_to(DIR_MERGED + 'companies.merged.json')
		#merge_man	= path_from_cwd_to(DIR_MERGED + 'companies.manual.json')
		filename_master	= path_from_cwd_to(DIR_MERGED + 'companies.json')
		#data_merged	= json.dumps(business_index.merge_autom, indent=4, sort_keys=True)
		#data_manual	= json.dumps(business_index.merge_manual, indent=4, sort_keys=True)
		master_list	= json.dumps(Combine.companies, cls=BusinessEncoder, indent=4, sort_keys=True)
		write_file(filename_master, master_list)
		#stats(business_index.get_list())
		#update(merge_man,	data_manual)
		#update(merge_auto,	data_merged)


	

	@staticmethod
	def stats(colist):
		stats = {}
		sources = [ 'src_bbb', 'src_homeadvisor', 'src_houzz', 'src_porch', 'src_yelp']

		for business in colist:
			source_nr = 0
			for k in business.__dict__.keys():
				if k in sources: source_nr = source_nr + 1
			if business.__dict__.get('contested'):
				stats['contested'] = stats.get('contested', 0) + 1
				for k, v in business.__dict__.get('contested'):
					if k == 'addr': stats['contested_addr'] = stats.get('contested_addr', 0) + 1
					if k == 'src_logo': stats['contested_logo'] = stats.get('contested_logo', 0) + 1
					if k == 'src_houzz': stats['contested_houzz_link'] = stats.get('contested_houzz_link', 0) + 1
					if k == 'src_bbb': stats['contested_bbb_link'] = stats.get('contested_bbb_link', 0) + 1
					if k == 'src_homeadvisor': stats['contested_homeadv_link'] = stats.get('contested_homeadv_link', 0) + 1
					if k == 'src_porch': stats['contested_porch_link'] = stats.get('contested_porch_link', 0) + 1

			if business.__dict__.get('src_bbb'): stats['source_bbb'] = stats.get('source_bbb', 0) + 1
			if business.__dict__.get('src_houzz'): stats['source_houzz'] = stats.get('source_houzz', 0) + 1
			if business.__dict__.get('src_porch'): stats['source_porch'] = stats.get('source_porch', 0) + 1
			if business.__dict__.get('src_homeadvisor'): stats['source_home_adv'] = stats.get('source_home_adv', 0) + 1
			if business.__dict__.get('src_yelp'): stats['source_yelp'] = stats.get('source_yelp', 0) + 1


			if business.__dict__.get('addr'): stats['has_addr'] = stats.get('has_addr', 0) + 1
			if business.__dict__.get('src_www'): stats['has_website'] = stats.get('has_website', 0) + 1
			if business.__dict__.get('phone'): stats['has_phone'] = stats.get('has_phone', 0) + 1
			if business.__dict__.get('src_logo'): stats['has_logo'] = stats.get('has_logo', 0) + 1

			if (source_nr == 1): stats['sources_1'] = stats.get('sources_1', 0) + 1
			elif (source_nr == 2): stats['sources_2'] = stats.get('sources_2', 0) + 1
			elif (source_nr == 3): stats['sources_3'] = stats.get('sources_3', 0) + 1
			elif (source_nr == 4): stats['sources_4'] = stats.get('sources_4', 0) + 1
			elif (source_nr == 5): stats['sources_5'] = stats.get('sources_5', 0) + 1
			else:
				stats['source_wtf'] = stats.get('source_wtf', 0) + 1
				pp(business.__dict__)

		pp(stats)



def write_file(filename, content):
	fp = None
	try:
		fp = open(filename, 'w+')
		fp.truncate()
		fp.write(content)
	except Exception as e:
		print e
	finally:
		if (fp): fp.close()
	

