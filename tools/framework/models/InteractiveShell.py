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

import cmd
from models		import *
from sources	import *
from pprint import pprint as pp

class InteractiveShell(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = 'SC > '
		self.source = {}
	#	source['bbb']	= BBB()
		self.source['factual']	= Factual()
	#	source['home']	= HomeAdvisor()
	#	source['houzz']	= Houzz()
	#	source['porch']	= Porch()
	#	source['yelp'] = Yelp()

	
	def do_load(self, line):
		for key in self.source.keys():
			if key == line.strip():
				src = self.source[key]
				src.get_company_index()
				# access with src.companies

	def do_find(self, line):
		for src in self.source.values():
			company = src.co_index.get(line)
			if (company): pp(company)

	def do_EOF(self, line):
		return True
