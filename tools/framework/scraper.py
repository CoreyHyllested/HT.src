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
from bs4 import BeautifulSoup as Soup
from pprint		import pprint as pp
from datetime	import datetime as dt 
from sources	import *
from models		import *
from controllers import *


VERSION = 0.34
BOT_VER = 0.8
THREADS	= 1
SECONDS = 85

dl_queue = []
threads	= []



def config_urllib():
	# configure the network.
	def create_connection(address, timeout=None, source_address=None):
		sock = socks.socksocket()
		sock.connect(address)
		return sock

	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket
	socket.create_connection = create_connection


	# setup user-agent information
	bot_id = 'SoulcraftingBot/v%d' % BOT_VER
	ua = urllib2.build_opener()
	ua.addheaders = [('User-agent', bot_id)]
	return ua


	

def dump_ss_uris():
	print 'URIs: (%d)' % len(dl_queue)
	for doc in dl_queue: print doc.uri
	print 



def prime_queue(ua, update_directories):
#	prime_queue_with_yelp(ua, update_directories)
	prime_queue_with_bbb(ua, update_directories)
	random.shuffle(dl_queue, random.random)
	#dump_ss_uris()

	q = Queue.Queue()
	for document in dl_queue:
		q.put(document)
	return q



def prime_queue_with_yelp(ua, update_dirs):
	yelp = Yelp(ua)
	companies = yelp.get_company_directory(update=update_dirs)
	print 'SCraper - got Yelp companies, update? %d' % (len(companies))



def prime_queue_with_bbb(ua, update_dirs):
	bbb = BBB(ua)

	companies = bbb.get_company_directory(update=update_dirs)	#set to args.update
	print 'SCraper - get all companies in BBB directory (%d)' % len(companies)
	for business in companies:
		bbb_url	= business.get('src_bbb')
		if (bbb_url):
			document = Document(business['src_bbb'], doc_type=DocumentType.BBB_BUSINESS)
			dl_queue.append(document)
#		else:
#			print 'Weird, missing src_bbb'
#			print 'Name %s, %s %s' % (business.get('name'), business.get('phone'), business.get('email'))
#			print 'Addr %b, %s' % (business.get('addr'), business.get('src_logo'))



if __name__ == '__main__':
	print 'SCraper v' + str(VERSION)
	#print 'ensure tor is running on :9050'
	parser = argparse.ArgumentParser(description='Scrape, normalize, and process information')
	parser.add_argument('-V', '--verbose',	help="increase output verbosity",	action="store_true")
	parser.add_argument('-U', '--update',	help='Check all business directories for updates',	action="store_true")
	args = parser.parse_args()
	if (args.verbose): print 'SCraper - verbosity enabled.'
	if (args.update): print 'SCraper - update company directory.' 

	create_directories()
	ua = config_urllib()

	q = prime_queue(ua, args.update)
	for thread_id in xrange(THREADS):
		t = ScraperThread(q, ua, id=thread_id, seconds=SECONDS, debug=False)
		t.start()
		threads.append(t)

	for thread in threads:
		thread.join()

