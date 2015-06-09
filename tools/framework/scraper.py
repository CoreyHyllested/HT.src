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

import sys, os, threading, argparse
import socks, socket, urllib2
import re, random, time
import Queue
from multiprocessing import Process
from bs4 import BeautifulSoup, Comment
from pprint		import pprint as pp
from datetime	import datetime as dt 
from sources	import *
from models		import *
from controllers import *
import requests


VERSION = 0.65
BOT_VER = 0.8
THREADS	= 1
SECONDS = 85

dl_queue = []
threads	= []



def config_urllib():
	# configure the network.
	pre_response = requests.get('http://icanhazip.com')

	def create_connection(address, timeout=None, source_address=None):
		sock = socks.socksocket()
		sock.connect(address)
		return sock

	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket
	socket.create_connection = create_connection

	post_response = requests.get('http://icanhazip.com')
	print 'SCraper - real IP: %s\ttor IP: %s ' % (pre_response._content.rstrip(), post_response._content.rstrip())
	if (pre_response._content == post_response._content): print 'SCraper - Not running tor:9050; likely to fail'

	# setup user-agent information
	ua = urllib2.build_opener()
	#ua_string = 'SoulcraftingBot/v%d' % BOT_VER
	ua_string = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
	ua.addheaders = [('User-agent', ua_string)]
	return ua




def dump_ss_uris():
	print 'URIs: (%d)' % len(dl_queue)
	for doc in dl_queue: print doc.uri
	print 


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



def load_sources(ua, config_params):
	bbb = BBB(ua)
	home = HomeAdvisor(ua)
	houzz = Houzz(ua)
	porch = Porch(ua)
	yelp = Yelp(ua)

	if (config_params.combine):
		business_index = BusinessIndex('main')
		print 'combining'

		for bus_info in bbb.get_company_directory():
			try:
				business = Business(bus_info)
				business_index.insert(business)
			except Exception as e:
				print e
		for bus_info in yelp.get_company_directory():
			try:
				business = Business(bus_info)
				business_index.insert(business)
			except Exception as e:
				print e
		for bus_info in houzz.get_company_directory():
			try:
				business = Business(bus_info)
				business_index.insert(business)
			except Exception as e:
				print e
		for bus_info in home.get_company_directory():
			try:
				business = Business(bus_info)
				business_index.insert(business)
			except Exception as e:
				print e


		print 'Merged Auto', len(business_index.merge_autom)
		print 'Merge Manual', len(business_index.merge_manual)
		print 'combined', len(business_index.index)
		merge_auto	= path_from_cwd_to(DIR_MERGED + 'companies.merged.json')
		merge_man	= path_from_cwd_to(DIR_MERGED + 'companies.manual.json')
		merged_co	= path_from_cwd_to(DIR_MERGED + 'companies.json')
		data_merged	= json.dumps(business_index.merge_autom, indent=4, sort_keys=True)
		data_manual	= json.dumps(business_index.merge_manual, indent=4, sort_keys=True)
		full_colist = json.dumps(business_index.index, cls=BusinessEncoder, indent=4, sort_keys=True)
		stats(business_index.get_list())
		#update(merge_list, full_co_list)

		update(merged_co,	full_colist)
		update(merge_man,	data_manual)
		update(merge_auto,	data_merged)
#		pp(business_index.auto_merged)

		#for k, v in business_index.index.iteritems():
		#	pp(v.__dict__)
		#pp(bbb.get_company_directory())
		#pp(home.get_company_directory())
		#pp(houzz.get_company_directory())
#		(yelp.get_company_directory())
		sys.exit(1);

	prime_queue_with_source(bbb, DocType.BBB_BUSINESS, config_params)
	prime_queue_with_source(home, DocType.HOME_BUSINESS, config_params)
	prime_queue_with_source(houzz, DocType.HOUZZ_BUSINESS, config_params)
	prime_queue_with_source(porch, DocType.PORCH_BUSINESS, config_params)
	prime_queue_with_source(yelp, DocType.YELP_BUSINESS, config_params)
	random.shuffle(dl_queue, random.random)
	#dump_ss_uris()

	q = Queue.Queue()
	for document in dl_queue:
		q.put(document)
	print 'SCraper - queue size %d' % (q.qsize())
	return q




def prime_queue_with_source(source, document_type, config_params):
	if ((config_params.source) and (config_params.source != source.SOURCE_TYPE)): return

	print 'SCraper - load %s directory' % (source.SOURCE_TYPE)
	directory = source.get_company_directory(update=config_params.update)
	for business in directory:
		uri = business.get('src_' + source.SOURCE_TYPE.lower())
		if (uri):
			document = Document(uri, source, doc_type=document_type)
			dl_queue.append(document)
	print 'SCraper - loaded %s directory. (%d businesses)' % (source.SOURCE_TYPE, len(directory))




if __name__ == '__main__':
	print 'SCraper v' + str(VERSION)
	parser = argparse.ArgumentParser(description='Scrape, normalize, and process information')
	parser.add_argument('-V', '--verbose',	help="increase output verbosity",	action="store_true")
	parser.add_argument('-C', '--combine',	help='Combine all company directories.',	action="store_true")
	parser.add_argument('-U', '--update',	help='Check all business directories for updates',	action="store_true")
	parser.add_argument('-S', '--source',	help='Single source [BBB, HomeAdvisor, Houzz, Porch, Yelp]')
	args = parser.parse_args()
	if (args.verbose):	print 'SCraper - verbosity enabled.'
	if (args.combine):	print 'SCraper - combining data sources'
	if (args.update):	print 'SCraper - update company directory.'
	if (args.source):	print 'SCraper - single source', args.source

	create_directories()
	ua = config_urllib()

	q = load_sources(ua, args)
	for thread_id in xrange(THREADS):
		print 'SCraper - starting thread %d' % (thread_id)
		t = ScraperThread(q, ua, id=thread_id, seconds=SECONDS, debug=True)
		t.start()
		threads.append(t)

	for thread in threads:
		thread.join()

	sys.exit()
