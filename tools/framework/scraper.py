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
from bs4 import BeautifulSoup, Comment
from bs4 import BeautifulSoup as Soup
from pprint		import pprint as pp
from datetime	import datetime as dt 
from sources	import *
from models		import *


VERSION = 0.15
BOT_VER = 0.8
THREADS	= 2
SECONDS = 1		#CHANGE to 90

DIR_RAWHTML = '/data/raw/'
DIR_REVIEWS	= '/data/reviews/'
DIR_SOURCES	= '/data/sources/'
ss_uris	= []
threads = []


def create_directories():
	safe_mkdir_local(DIR_RAWHTML)
	#safe_mkdir_local(DIR_REVIEWS)
	safe_mkdir_local(DIR_SOURCES)
	print 'created directories'


def config_urllib():
	# configure the network.
	def create_connection(address, timeout=None, source_address=None):
		sock = socks.socksocket()
		sock.connect(address)
		return sock

	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket
	socket.create_connection = create_connection


	bot_id = 'SoulcraftingBot/v%d' % BOT_VER
	ua = urllib2.build_opener()
	ua.addheaders = [('User-agent', bot_id)]
	return ua


def safe_mkdir_local(path):
	directory = os.getcwd() + path
	safe_mkdir(directory)


def safe_mkdir(directory):
	if (os.path.exists(directory) == False):
		os.makedirs(directory)


def open_file(path_from_cwd):
	filename = os.getcwd() + path_from_cwd
	print 'creating file ' + str(filename)
	fp = open(filename, 'a+')
	return fp


def create_review(review_id):
	fn = '/data/reviews/' + review_id 
	fp = open_file(fn)
	fp.truncate()
	return fp

	


def dump_ss_uris():
	print 'URIs: (%d)' % len(ss_uris)
	for ss in ss_uris:
		print ss.uri
	print 



def prime_queue():
	prime_queue_with_bbb()
	random.shuffle(ss_uris, random.random)
	dump_ss_uris()

	q = Queue.Queue()
	for ss in ss_uris:
		q.put(ss)
	return q



def prime_queue_with_bbb():
	source_bbb = BBB()
	uris_bbb = source_bbb.get_company_directory()
	for uri in uris_bbb:
		print 'uri from uris_bbb', uri
		ss = Snapshot(uri)
		ss_uris.append(ss)
	ss_uris.append(Snapshot("https://linkedin.com/"))
	ss_uris.append(Snapshot("https://google.com/"))
	ss_uris.append(Snapshot("http://www.jsonline.com/"))







if __name__ == '__main__':
	print 'SCraper v' + str(VERSION)
	#print 'ensure tor is running on :9050'
	parser = argparse.ArgumentParser(description='Scrape, normalize, and process information')
	parser.add_argument('-V', '--verbose',	help="increase output verbosity",	action="store_true")
	parser.add_argument('-U', '--update',	help="Update business directory",	action="store_true")
	args = parser.parse_args()
	if (args.verbose):
		print 'verbosity is on'
	if (args.update):
		print 'Update business directory!'
	
	create_directories()
	ua = config_urllib()

	q = prime_queue()
	for thread_id in xrange(THREADS):
		t = ScraperThread(q, ua, id=thread_id)
		t.start()
		threads.append(t)
	
	for thread in threads:
		thread.join()
	

