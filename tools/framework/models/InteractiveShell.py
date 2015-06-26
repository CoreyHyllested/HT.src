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
		self.collisions = None
		self.bi	= None
		self.op_business = None

	
	def __load_collisions(self):
		if (not self.bi): self.bi = BusinessIndex()
		self.idx_collisions = self.bi.get_collisions_index()
		self.k_collision = None
		self.v_collision = None
		self.nr_collision = 0

		nr_total_collisions = 0
		for b in self.idx_collisions.values():
#			print 'inspect %s business, has %d collisions' % (b.business_name, len(b.get_collisions()))
			nr_total_collisions = nr_total_collisions + len(b.get_collisions())
		print 'loaded %d businesses with %d collisions' % (len(self.idx_collisions), nr_total_collisions)


	def __get_collision(self, id=None):
		if (not id):
			(self.k_collision, self.v_collision) = self.idx_collisions.items()[self.nr_collision]
			if (self.v_collision):
				# update the operational business.
				self.op_business = self.v_collision
				print self.v_collision._id, self.v_collision.business_name, len(self.v_collision.get_collisions()), 'collisions'
			return self.v_collision
		return self.idx_collisions.get(id)

	def __get_prev_collision(self):
		self.nr_collision = self.nr_collision - 1
		return self.__get_collision()

	def __get_next_collision(self):
		self.nr_collision = self.nr_collision + 1
		return self.__get_collision()

	def do_load(self, line):
		for key in self.source.keys():
			if key == line.strip():
				src = self.source[key]
				src.get_company_index()
				# access with src.companies


	def do_getcollisions(self, line):
		if (not self.collisions): self.__load_collisions()

		if (line == ''):
			# save to re-run / re-use
			self.__get_collision()


	def do_next(self, line):
		if (not self.collisions):
			print 'run collisions first'
			return
		b = self.__get_next_collision()
		print b._id, b.business_name


	def do_emails(self, line):
		if (not self.op_business):
			print 'No business selected'
			return
		print self.op_business._id, self.op_business.contact_email()


	def do_collisions(self, line):
		if (not self.op_business):
			print 'No business selected'
			return

		nr = -1
		try:
			if (line != ''):
				nr = int(line)
				print 'get', nr
		except Exception as e:
			pass


		collisions = self.op_business.get_collisions()
		print self.op_business._id, len(collisions), 'collisions'
		if (collisions and nr >= 0):
			nr = min(nr, len(collisions))
			collisions = [ collisions.items()[nr] ]

		for c in collisions.values():
			print 'Collision: %s (%d) %r' % (c['name'], c['attr']['name'], c['id'])
			print '\taddress:', c['attr']['address']
			print '\twebsite:', c['attr']['website']
			print '\tcontact:', 'Email', c['attr']['email'], 'Phone', c['attr']['phone']


	def do_name(self, line):
		if (not self.op_business):
			print 'No business selected'
			return
		print self.op_business._id, self.op_business.business_name

	def do_phones(self, line):
		if (not self.op_business):
			print 'No business selected'
			return
		print self.op_business._id, self.op_business.contact_phone()

	def do_sources(self, line):
		if (not self.op_business):
			print 'No business selected'
			return
		print self.op_business._id, self.op_business.business_name
		pp(self.op_business.get_sources())

	def do_website(self, line):
		if (not self.op_business):
			print 'No business selected'
			return
		print self.op_business._id, self.op_business.business_website


	def do_find(self, line):
		for src in self.source.values():
			company = src.co_index.get(line)
			if (company): pp(company)

	def do_EOF(self, line):
		return True
