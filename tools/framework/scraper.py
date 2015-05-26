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
import re, random, time
import threading
import Queue
from bs4 import BeautifulSoup, Comment
from bs4 import BeautifulSoup as Soup
from pprint		import pprint as pp
from datetime	import datetime as dt 

BOT_VER = 0.8
VERSION = 0.7
THREADS	= 2

URIS = []
DIR_RAWHTML = '/data/raw/'
DIR_REVIEWS	= '/data/reviews/'
threads = []


def create_directories():
	safe_mkdir_local(DIR_RAWHTML)
	safe_mkdir_local(DIR_REVIEWS)
	print 'Created directories'

def config_urllib():
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

	


def dump_uris():
	print 'URIs: (%d)' % len(URIS)
	pp(URIS)
	print 

def get_googlecache(URI):
	return 'https://webcache.googleusercontent.com/search?q=cache:' + strip_http(URI)

def setup_useragent():
	UA='SoulcraftBot'
	return UA

def get_bbb_types_cached_test():
	return [ "http://www.bbb.org/denver/accredited-business-directory/deck-builder" ]


def prime_queue():
	#dump_uris()
	URIS.append ('http://twitter.com')
	URIS.append ('https://google.com')
	URIS.append ('http://linkedin.com')
	URIS.append ('https://127.0.0.1:5000/')
	URIS.append ('https://soulcrafting.co/')
	URIS.append ('http://www.lastfm.com')
	random.shuffle(URIS, random.random)
	#dump_uris()
	q = Queue.Queue()
	for uri in URIS:
		q.put(uri)
	return q



def recent_snapshot_exists(directory, days=30):
	if os.path.exists(directory) is False: 
		print directory, 'does not exist.  download document.'
		return False

	for fp in os.listdir(directory):
		if (os.path.isdir(directory + '/' + fp) is False):
			continue

		timedelta = dt.now() - dt.strptime(fp, '%Y-%m-%d')
		if (timedelta.days < days):
			#print directory + '/' + fp + ' is ' + str(timedelta.days) + ' old, and within ' + str(days) + ' window'
			return True
	print 'update snapshot'
	return False



def strip_http(uri):
	if 'https://' in uri[0:8]:
		return uri[8:]
	if 'http://' in uri[0:7]:
		return uri[7:]



def get_snapshot(useragent, uri):
	print 'collect page:', uri
	
	# does page already exist?, do I need to escape URI?
	directory = os.getcwd() + DIR_RAWHTML + strip_http(uri)
	ts = dt.now().strftime('%Y-%m-%d')
#	print directory, ts

	try:
		snapshot = recent_snapshot_exists(directory, days=7)
		if (snapshot == False): 
			doc = useragent.open(uri).read()
			save_document(uri, doc, directory + '/' + ts)
	except Exception as e:
		print e
	

	



def save_document(uri, document, directory):
	safe_mkdir(directory)

	try:
		# saving full, raw document
		fp = open(directory + '/document.html', 'w+')
		fp.truncate()
		fp.write(document)
	except Exception as e:
		print e
	finally:
		if (fp): fp.close()



class Scrape(threading.Thread):

	def __init__(self, q, agent, id):
		self.q	= q
		self.ua	= agent
		self.id	= id
		threading.Thread.__init__(self)

	def run(self):
		while not q.empty():
			page = q.get()
			print 'Thread: get ' + str(page)
			get_snapshot(self.ua, page)
			print 'Thread: finished'
			time.sleep(10);
		




if __name__ == '__main__':

	print 'SCraper v' + str(VERSION)
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
		t = Scrape(q, ua, id=thread_id)
		t.start()
		threads.append(t)
	
	for thread in threads:
		thread.join()
	



