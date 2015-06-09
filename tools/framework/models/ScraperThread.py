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


import threading, time
import random
import Queue
from . import Snapshot
from pprint		import pprint as pp
from datetime	import datetime as dt 


class ScraperThread(threading.Thread):
	def __init__(self, q, id, debug=False):
		threading.Thread.__init__(self)
		self.q	= q
		self.id	= id
		self.debug	= debug
		self.total_docs	= q.qsize()
		self.downloaded = 0
		self.dl_attempt	= 0


	def run(self):
		while not self.q.empty():
			document = self.q.get()
			self.dl_attempt = self.dl_attempt + 1
			if (self.debug): print 'Thread(%d): %d|%d|%d\t%s' % (self.id, self.downloaded, self.dl_attempt, self.total_docs, document.uri)
			doc_ts = dt.now()
			saved = document.get_document()
			if (saved):
				self.downloaded = self.downloaded + 1
				ts_diff = dt.now() - doc_ts
				if (self.debug): print 'Thread(%d): %d|%d|%d\t%s' % (self.id, self.downloaded, self.dl_attempt, self.total_docs, ts_diff)

