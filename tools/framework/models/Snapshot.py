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
import requests, urllib2, socks, socket
import re, random, time, json
import Queue
from pprint		import pprint as pp
from datetime	import datetime as dt 
from controllers import *


class DocType(object):
	UNKNOWN		= 0

	BBB_DIRECTORY	= 0x11
	BBB_BUSINESS	= 0x12
	BBB_REVIEW		= 0x14
	YELP_BUSINESS	= 0x22
	HOME_DIRECTORY	= 0x31
	HOME_BUSINESS	= 0x32
	HOUZZ_DIRECTORY	= 0x41
	HOUZZ_BUSINESS	= 0x42
	PORCH_DIRECTORY	= 0x51
	PORCH_BUSINESS	= 0x52

	JSON_METADATA	= 0xFF

	LOOKUP_TABLE = {
		BBB_DIRECTORY	: 'BBB_DIRECTORY',
		BBB_BUSINESS	: 'BBB_BUSINESS',
		BBB_REVIEW		: 'BBB_REVIEW',

		YELP_BUSINESS	: 'YELP_BUSINESS',

		HOME_DIRECTORY	: 'HOME_ADV_DIRECTORY',
		HOME_BUSINESS	: 'HOME_ADV_BUSINESS',

		HOUZZ_DIRECTORY	: 'HOUZZ_DIRECTORY',
		HOUZZ_BUSINESS	: 'HOUZZ_BUSINESS',

		PORCH_DIRECTORY	: 'PORCH_DIRECTORY',
		PORCH_BUSINESS	: 'PORCH_BUSINESS',


		UNKNOWN			: 'UNKNOWN',
		JSON_METADATA	: 'JSON_METADATA'
	}

	@staticmethod
	def name(state):
		return DocType.LOOKUP_TABLE.get(state, 'UNDEFINED')





class DocState(object):
	EMPTY		= 0
	READ_WWW	= 0x200
	READ_CACHE	= 0x201
	READ_FAIL	= 0x404




class Document(object):
	errors = {}
	ratelimited = Queue.Queue()
	DIR_RAWHTML = os.getcwd() + '/data/raw/'

	def __init__(self, uri, source, doc_type=None, force_webcache=False):
		self.uri = uri
		if (source):
			self.location = self.DIR_RAWHTML + url_clean(uri)
			self.webcache = webcache_url(uri)
			self.use_webcache = force_webcache
		self.filename = 'document.html'
		self.doc_type	= doc_type
		self.doc_state	= DocState.EMPTY
		self.doc_source	= source
		self.content = None
	


	
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



	def get_document(self, debug=False):
		# check if a recent document already exists?
		if (debug): print '\n%s.get_document(%r)' % (self.doc_source.SOURCE_TYPE, self)
		snapshot_file = self.snapshot_exists(days=7)
		if (snapshot_file): return self.read_cache(debug)

		try:
			self.download(debug)
			self.write_cache(debug)
		except Exception as e:
			print e
			print 're-raising'
			#raise e
		return True



	def __read_cache_path(self):
		# for metadata, files should ALWAYS exist.
		if self.doc_type == DocType.JSON_METADATA:
			return self.location + '/' + self.filename
		return self.snapshot_exists(days=365)



	def __write_cache_path(self):
		if self.doc_type == DocType.JSON_METADATA:
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
				if (debug): print '%s.reading cache...' % (self.doc_source.SOURCE_TYPE)
				fp = open(file_path, 'r')
				self.content	= fp.read()
				self.doc_state	= DocState.READ_CACHE
			except Exception as e:
				print e
			finally:
				if (fp): fp.close()



	def download(self, debug=False):
		if (debug): print '%s.download doc' % (self.doc_source.SOURCE_TYPE)
		self.doc_state	= DocState.READ_FAIL

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
					#raise Exception('WEBCACHE-FAILED')
			if (response._content): 
				self.content	= response._content
				self.doc_state	= DocState.READ_WWW
			else:
				print 'Something fucked up'
				print 'status code(%d|%s) elapsed %s, encoding %s' % (response.status_code, response.reason, response.elapsed, response.encoding)
				pp(response.headers)
		except requests.exceptions.HTTPError as e:
			print 'HTTPError %d: %s' % (response.status_code, self.uri)
			self.doc_source.add_error('HTTPError', self.uri)
			print e
		except requests.exceptions.ConnectionError as e:
			print e
			self.doc_source.add_error('ConnectionError', self.uri)
		except Exception as e:
			print 'General Exception'
			self.doc_source.add_error('download_failed', self.uri)
			print type(e), e
			print 'content:', response._content
		finally:
			# hit URL, always sleep
			self.doc_source.sleep()





	def write_cache(self, debug=False):
		if (not self.content): return

		try:
			# saving raw content
			file_path = self.__write_cache_path()
			if (debug): print '%s.caching file %s' % (self.doc_source.SOURCE_TYPE, file_path)
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
		return '<Document %r %r>'% (self.uri, DocType.name(self.doc_type))

	def __str__ (self):
		return '<Document %r %r>'% (self.uri, DocType.name(self.doc_type))

