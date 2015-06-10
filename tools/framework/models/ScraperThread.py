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
		self.doc_total	= q.qsize()
		self.doc_count	= 0
		self.doc_error	= 0
		self.doc_dload	= 0


	def run(self):
		while not self.q.empty():
			ts = dt.now()
			document = self.q.get()
			document.get_document()
			ts_diff = dt.now() - ts

			self.doc_count = self.doc_count + 1
			if (document.doc_state == 0x200):	self.doc_dload = self.doc_dload + 1
			if (document.doc_state & 0x400):	self.doc_error = self.doc_error + 1
			print 'Thread(%d): %d %d|%d|%d\t%s\t%s' % (self.id, self.doc_total, self.doc_count, self.doc_error, self.doc_dload, ts_diff, document.uri)



