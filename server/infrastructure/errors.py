import sys
from datetime import datetime as dt


#IndexError: list index out of range
#seen: we tried to index a list (from DB) that was zero


class NoProposalFound(Exception):
	def __init__(self, p_uuid, p_from):
		self.prop_uuid = p_uuid
		self.prop_from = p_from
		
	def __str__(self):
		return "Proposal (%s, %s) not found" % (self.prop_uuid, self.prop_from)


class InvalidCreditCard(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
