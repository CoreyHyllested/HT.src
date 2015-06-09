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
	def __init__(self, q, agent, id, seconds=90, debug=False):
		threading.Thread.__init__(self)
		self.q	= q
		self.ua	= agent
		self.id	= id
		self.seconds = seconds
		self.debug	= debug

	def run(self):
		while not self.q.empty():
			ss = self.q.get()
			if (self.debug): print 'Thread(%d): get %s' % (self.id, ss.uri)
			saved = ss.get_document()
			if (saved): time.sleep(self.seconds + random.randint(0, 10))

