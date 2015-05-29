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
import urllib2, json
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


	LOOKUP_TABLE = {
		UNKNOWN		: 'UNKNOWN',
		BBB_DIRECTORY	: 'BBB_DIRECTORY',
		BBB_BUSINESS	: 'BBB_BUSINESS',
		BBB_REVIEW		: 'BBB_REVIEW'
	}

	@staticmethod
	def name(state):
		return BBBDocument.LOOKUP_TABLE.get(state, 'UNDEFINED')





class Snapshot(object):
	errors = {}
	ratelimited = Queue.Queue()
	DIR_RAWHTML = os.getcwd() + '/data/raw/'

	def __init__(self, uri, doc_type=None, force_webcache=False):
		self.uri = uri
		self.webcache = webcache_url(uri)
		self.snap_dir = self.DIR_RAWHTML + url_clean(uri)
		self.document = None
		self.doc_type = doc_type
		self.use_webcache = force_webcache 



	def snapshot_exists(self, days=30):
		if os.path.exists(self.snap_dir) is False:
			return None

		last_ss = None
		last_ts = days
		for filename in os.listdir(self.snap_dir):
			if (os.path.isdir(self.snap_dir + '/' + filename) is False):
				continue

			timedelta = dt.now() - dt.strptime(filename, '%Y-%m-%d')
			if (timedelta.days < last_ts):
				last_ts = timedelta.days
				last_ss = self.snap_dir + '/' + filename + '/document.html'
		return last_ss



	def save_snapshot(self, useragent):
		# check if a recent snapshot already exists?
		snapshot_file = self.snapshot_exists(days=7)
		if (snapshot_file): return self.read_cache()

		print 'Thread()\tdownloading: %s' % (self.uri)
		try:
			self.dl_document(useragent)
			self.save_document()
		except Exception as e:
			print e
			raise e
		return True




	def read_cache(self):
		fp_content = None

		snapshot_file = self.snapshot_exists(days=90)
		if (snapshot_file):
			try:
				print 'Thread()\tloading cache of %s' % (self.uri)
				fp = open(snapshot_file, 'r')
				self.document = fp.read()
			except Exception as e:
				print e
			finally:
				if (fp): fp.close()


	def dl_webcache(self):
		pass


	def dl_document(self, useragent):
		try:
			document = useragent.open(self.uri).read()

			# if document was rate limited, try using the webcache
			if 'Sorry, we had to limit your access to this website.' in document:
				self.ratelimited.put(self.uri)
				print 'rate-limited: %d times, retry with %s' % (len(self.ratelimited.qsize()), self.webcache)
				document = useragent.open(self.webcache).read()

			if (document): self.document = document
		except urllib2.HTTPError as e:
			print e
			self.errors[e.geturl()] = e.code
		except Exception as e:
			print type(e), e
		return self.document



	def save_document(self):
		fp = None
		if (not self.document): return 

		timestamp = dt.now().strftime('%Y-%m-%d')
		directory = self.snap_dir + '/' + str(timestamp)
		try:
			# saving full, raw document
			safe_mkdir(directory)
			fp = open(directory + '/document.html', 'w+')
			fp.truncate()
			fp.write(self.document)
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
		return '<Snapshot %r>'% (self.uri)

	def __str__ (self):
		return '<Snapshot %s>' % (self.uri)


#class SourceSnapshot(object):
#	def __init__(self, uri, snapshot_dir=None, force_webcache=False):
#		super(SourceSnapshot, self).__init__(self, uri, force_webcache=force_webcache)
#		self.snap_dir = snapshot_dir
#		print 'init SourceSnapshot, set dir = ', self.snap_dir, snapshot_dir
