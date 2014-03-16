import sys
from datetime import datetime as dt


#IndexError: list index out of range
#seen: we tried to index a list (from DB) that was zero

class DB_Error(Exception):
	def __init__(self, db_err, usr_msg):
		self.db_err  = db_err
		self.usr_msg = usr_msg

	def __str__(self):
		return "DB_ERR(%s, %s)" % (self.db_err, self.usr_msg)



class PermissionDenied(Exception):
	def __init__(self, task, usr, usr_msg):
		self.task = task
		self.usr  = usr
		self.msg  = usr_msg

	def __str__(self):
		return "PermissionError(%s, %s, %s)" % (self.task, self.usr, self.msg)



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
