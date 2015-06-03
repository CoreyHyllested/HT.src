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
import urllib2, requests
import json, random
from pprint import pprint as pp
from controllers import *



class Source(object):
	USE_WEBCACHE = False
	SECONDS = 90	# get from robots.txt
	SOURCE_DIR = ''
	SOURCE_TYPE	= 'UnknownSource'
	errors = {}
	ratelimited = []

	def __init__(self):
		pass
	
	def get_top_directory(self):
		return []
		
	def get_full_directory(self):
		return []

	def sleep(self):
		#print '%s.update_co_directory: (downloaded) so sleeping...' % (self.SOURCE_TYPE)
		time.sleep(self.SECONDS + random.randint(0, 10))


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

