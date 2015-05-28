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



class Snapshot(object):
	errors = {}
	ratelimited = Queue.Queue()
	DIR_RAWHTML = os.getcwd() + '/data/raw/'

	def __init__(self, uri, force_webcache=False):
		self.uri = uri
		self.webcache = webcache_url(uri)
		self.snap_dir = self.DIR_RAWHTML + url_clean(uri)
		self.document = None
		self.use_webcache = force_webcache 



	def snapshot_exists(self, days=30):
		if os.path.exists(self.snap_dir) is False:
			return False

		for filename in os.listdir(self.snap_dir):
			if (os.path.isdir(self.snap_dir + '/' + filename) is False):
				continue

			timedelta = dt.now() - dt.strptime(filename, '%Y-%m-%d')
			if (timedelta.days < days):
				#print self.snap_dir + '/' + fp + ' is ' + str(timedelta.days) + ' old, and within ' + str(days) + ' window'
				#maybe return the document itself?
				return True
		return False



	def save_snapshot(self, thread):
		# check if a recent snapshot already exists?
		snapshot_exists = self.snapshot_exists(days=7)
		if (snapshot_exists == True): return False

		print 'Thread(%d)\tdownloading: %s' % (thread.id, self.uri)
		try:
			self.dl_document(thread)
			self.save_document()
		except Exception as e:
			print e
		return True



	def get_snapshot(self):
		snapshot_exists = self.snapshot_exists(days=90)
		if (snapshot_exists == True): 
			#get file
			return 'File Exists, gotta write code'
		pass



	def dl_webcache(self):
		pass


	def dl_document(self, thread):
		try:
			document = thread.ua.open(self.uri).read()

			# if document was rate limited, try using the webcache
			if 'Sorry, we had to limit your access to this website.' in document:
				self.ratelimited.put(self.uri)
				print 'rate-limited: %d times, retry with %s' % (len(self.ratelimited.qsize()), self.webcache)
				document = thread.ua.open(self.webcache).read()

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

