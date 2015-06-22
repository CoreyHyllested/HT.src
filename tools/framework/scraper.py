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


VERSION = 0.78
BOT_VER = 0.8
THREADS	= 1

dl_queue = []
threads	= []



def config_urllib(args):
	if (args.combine):	return 
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
	print 'SCraper - real IP: %s\t TOR IP: %s ' % (pre_response._content.rstrip(), post_response._content.rstrip())
	if (pre_response._content == post_response._content): print 'SCraper - Not running tor:9050; likely to fail'

	# setup user-agent information
	ua = None #urllib2.build_opener()
	#ua = urllib2.build_opener()
	#ua_string = 'SoulcraftingBot/v%d' % BOT_VER
	#ua_string = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
	#ua.addheaders = [('User-agent', ua_string)]
	return ua





def load_sources(config_params):
	bbb = BBB()
	fact = Factual()
	home = HomeAdvisor()
	houzz = Houzz()
	porch = Porch()
	yelp = Yelp()

	if (config_params.combine):
		print 'Combine sources'
		#Business.add_source(bbb, config_params)
		Business.add_source(fact, config_params)
		#Combine.add_source(home, config_params)
		#Combine.add_source(houzz, config_params)
		#Combine.add_source(porch, config_params)
		#Combine.add_source(yelp, config_params)
		#Combine.save_output()
		sys.exit(1);

	prime_queue_with_source(bbb, DocType.BBB_BUSINESS, config_params)
	prime_queue_with_source(fact, DocType.FACT_BUSINESS, config_params)
	prime_queue_with_source(home, DocType.HOME_BUSINESS, config_params)
	prime_queue_with_source(houzz, DocType.HOUZZ_BUSINESS, config_params)
	prime_queue_with_source(porch, DocType.PORCH_BUSINESS, config_params)
	prime_queue_with_source(yelp, DocType.YELP_BUSINESS, config_params)
	random.shuffle(dl_queue, random.random)

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
	parser.add_argument('-S', '--source',	help='Single source [BBB, Factual, HomeAdvisor, Houzz, Porch, Yelp]')
	parser.add_argument('-D', '--duplicates',	help='When updating, check for duplicates', action="store_true")
	parser.add_argument('-M', '--master',	help='When updating, check for duplicates', action="store_true")
	args = parser.parse_args()
	if (args.verbose):	print 'SCraper - verbosity enabled.'
	if (args.combine):	print 'SCraper - combining data sources'
	if (args.update):	print 'SCraper - update company directory.'
	if (args.source):	print 'SCraper - single source', args.source

	create_directories()
	config_urllib(args)

	q = load_sources(args)
	for thread_id in xrange(THREADS):
		print 'SCraper - starting thread %d' % (thread_id)
		t = ScraperThread(q, id=thread_id, debug=True)
		t.start()
		threads.append(t)

	for thread in threads:
		thread.join()

	sys.exit()
