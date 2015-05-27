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
from sources	import *


VERSION = 0.11
BOT_VER = 0.8
THREADS	= 2
SECONDS = 1		#CHANGE to 90

DIR_RAWHTML = '/data/raw/'
DIR_REVIEWS	= '/data/reviews/'
DIR_SOURCES	= '/data/sources/'
dl_uris	= []
threads = []


def create_directories():
	safe_mkdir_local(DIR_RAWHTML)
	#safe_mkdir_local(DIR_REVIEWS)
	safe_mkdir_local(DIR_SOURCES)
	print 'created directories'


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
	print 'URIs: (%d)' % len(dl_uris)
	pp(dl_uris)
	print 


def get_googlecache(URI):
	return 'https://webcache.googleusercontent.com/search?q=cache:' + strip_http(URI)


def prime_queue():
	#dump_uris()
	prime_queue_with_bbb()
	random.shuffle(dl_uris, random.random)
	#dump_uris()
	q = Queue.Queue()
	for uri in dl_uris:
		q.put(uri)
	return q



def prime_queue_with_bbb():
	source_bbb = BBB()
	source_bbb.update_company_directory()
	dl_uris.append ("http://www.bbb.org/denver/accredited-business-directory/deck-builder")



def recent_snapshot_exists(directory, days=30):
	if os.path.exists(directory) is False: 
		return False

	for fp in os.listdir(directory):
		if (os.path.isdir(directory + '/' + fp) is False):
			continue

		timedelta = dt.now() - dt.strptime(fp, '%Y-%m-%d')
		if (timedelta.days < days):
			#print directory + '/' + fp + ' is ' + str(timedelta.days) + ' old, and within ' + str(days) + ' window'
			return True
	return False



def strip_http(uri):
	if 'https://' in uri[0:8]:
		return uri[8:]
	if 'http://' in uri[0:7]:
		return uri[7:]


def clean_uri(uri):
	uri = strip_http(uri)
	uri = re.sub('[/:]','_', uri)
	return uri


def get_snapshot(thread, uri):
	print 'Thread(%d)\tcollect page: %s' % (thread.id, uri)
	
	# does page already exist?, do I need to escape URI?
	directory = os.getcwd() + DIR_RAWHTML + clean_uri(uri)
	ts = dt.now().strftime('%Y-%m-%d')
	#print 'Thread(%d)\tdirectory %s/%s' % (thread.id, directory, ts)

	snapshot = recent_snapshot_exists(directory, days=7)
	if (snapshot == False): 
		print 'Thread(%d)\tdownloading: %s' % (thread.id, uri)
		try:
			document = dl_document(thread, uri)
			save_document(uri, document, directory + '/' + ts)
		except Exception as e:
			print e



def dl_document(thread, uri):
	user_agent = thread.ua
	document = user_agent.open(uri).read()
	webcache = get_googlecache(uri)

	if 'Sorry, we had to limit your access to this website.' in document:
		thread.ratelimited.append(uri)
		print 'Thread(%d)\trate-limited: %d times, retry with %s' % (thread.id, len(thread.ratelimited), webcache)
		document = user_agent.open(webcache).read()
	return document




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
		self.ratelimited = []
		threading.Thread.__init__(self)

	def run(self):
		while not q.empty():
			page = q.get()
			print 'Thread(%d): get %s' % (self.id, str(page))
			get_snapshot(self, page)
			#print 'Thread: finished'
			time.sleep(SECONDS);
		




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
	#for thread_id in xrange(THREADS):
	#	t = Scrape(q, ua, id=thread_id)
	#	t.start()
	#	threads.append(t)
	
	for thread in threads:
		thread.join()
	

