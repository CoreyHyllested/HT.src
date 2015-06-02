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


import sys, os, time
import requests, urllib2, json
import socks, socket
import re, random, time
import Queue
from pprint		import pprint as pp
from datetime	import datetime as dt 
from controllers import *


class DocumentType(object):
	UNKNOWN		= 0

	BBB_DIRECTORY	= 0x11
	BBB_BUSINESS	= 0x12
	BBB_REVIEW		= 0x14
	YELP_BUSINESS	= 0x22

	HOUZ_DIRECTORY	= 0x31
	HOUZ_BUSINESS	= 0x32

	JSON_METADATA	= 0xFF

	LOOKUP_TABLE = {
		UNKNOWN		: 'UNKNOWN',
		BBB_DIRECTORY	: 'BBB_DIRECTORY',
		BBB_BUSINESS	: 'BBB_BUSINESS',
		BBB_REVIEW		: 'BBB_REVIEW',
		YELP_BUSINESS	: 'YELP_BUSINESS',
		HOUZ_DIRECTORY	: 'HOUZZ_DIRECTORY',
		HOUZ_BUSINESS	: 'HOUZZ_BUSINESS',
		JSON_METADATA	: 'JSON_METADATA'
	}

	@staticmethod
	def name(state):
		return BBBDocument.LOOKUP_TABLE.get(state, 'UNDEFINED')





class Document(object):
	errors = {}
	ratelimited = Queue.Queue()
	DIR_RAWHTML = os.getcwd() + '/data/raw/'

	def __init__(self, uri, doc_type=None, force_webcache=False):
		self.uri = uri
		if (uri):
			self.webcache = webcache_url(uri)
			self.location = self.DIR_RAWHTML + url_clean(uri)
		self.filename = 'document.html'
		self.doc_type = doc_type
		self.content = None
		self.use_webcache = force_webcache 


	
	def snapshot_exists(self, days=30):
		if os.path.exists(self.location) is False:
			return None

		last_ss = None
		last_ts = days
		for dir_name in os.listdir(self.location):
			if (os.path.isdir(self.location + '/' + dir_name) is False):
				continue

			timedelta = dt.now() - dt.strptime(dir_name, '%Y-%m-%d')
			if (timedelta.days < last_ts):
				last_ts = timedelta.days
				last_ss = self.location + '/' + dir_name + '/' + self.filename
		return last_ss



	def get_document(self):
		# check if a recent document already exists?
		snapshot_file = self.snapshot_exists(days=7)
		if (snapshot_file): return self.read_cache()

		try:
			print '\tdownload document %s' % (self.uri)
			self.download()
			self.write_cache()
		except Exception as e:
			print e
			raise e
		return True



	def __read_cache_path(self):
		# for metadata, files should ALWAYS exist.
		if self.doc_type == DocumentType.JSON_METADATA:
			return self.location + '/' + self.filename
		return	self.snapshot_exists(days=365)



	def __write_cache_path(self):
		if self.doc_type == DocumentType.JSON_METADATA:
			return self.location + '/' + self.filename

		timestamp = dt.now().strftime('%Y-%m-%d')
		directory = self.location + '/' + str(timestamp)
		safe_mkdir(directory)
		return directory + '/' + self.filename



	def read_cache(self, debug=False):
		file_path = self.__read_cache_path()
		if (file_path):
			fp = None
			try:
				if (debug): print '\t\tloading cache... %s' % (self.uri)
				fp = open(file_path, 'r')
				self.content = fp.read()
			except Exception as e:
				print e
			finally:
				if (fp): fp.close()



	def download(self):
		try:
			s = requests.Session()
			response = s.get(self.uri)
			response.raise_for_status()

			# check document for any rate-limited message, if so, try using the webcache
			if 'Sorry, we had to limit your access to this website.' in response._content:
				self.ratelimited.put(self.uri)
				print 'rate-limited: %d times, retry with %s' % (len(self.ratelimited.qsize()), self.webcache)
				response = s.get(self.webcache)
				if 'Sorry, we had to limit your access to this website.' in response._content:
					print 'Rate limited again.'
					raise Exception('WEBCACHE-FAILED')
			content = response._content

			if (content): self.content = content
		except requests.exceptions.HTTPError as e:
			print '%d: %s' % (response.status_code, self.uri)
			print e
		except Exception as e:
			print e
#content = useragent.open(self.uri).read()
#		except urllib2.HTTPError as e:
#			print e
#			self.errors[e.geturl()] = e.code
#		except Exception as e:
#			print type(e), e
		return self.content





	def write_cache(self):
		if (not self.content): return

		try:
			# saving raw content
			file_path = self.__write_cache_path()
			print '\tcaching document: %s' % (file_path)
			fp = open(file_path, 'w+')
			fp.truncate()
			fp.write(self.content)
		except Exception as e:
			print e
		finally:
			if (fp): fp.close()




	def read_json_file(self, rel_file_path, DEBUG=False):
		# FOR TESTING.  http://jsonlint.com/
		try:
			file_pointer = open (os.getcwd() + rel_file_path, 'r')
			file_content = file_pointer.read()
			json_content = json.loads(file_content)
			if (DEBUG): pp(json_content)
			#directory = data.get('directory', [])
			return json_content
		except Exception as e:
			print str(e)
		finally:
			if (file_pointer): file_pointer.close()
		return { "data" : None }



	def __repr__ (self):
		return '<Document %r>'% (self.uri)

	def __str__ (self):
		return '<Document %s>' % (self.uri)

