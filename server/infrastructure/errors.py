import sys
from datetime import datetime as dt


#IndexError: list index out of range
#seen: we tried to index a list (from DB) that was zero

class Sanitized_Exception(Exception):
	def __init__(self, caught, msg=None):
		self.caught = caught
		self.sanitized_msg = 'Ooops'
		if (msg): self.sanitized_msg = msg
	
	def orig_error(self):
		return self.caught
	
	def sanitized_msg(self):
		return self.sanitized_msg



class StateTransitionError(Exception):
	def __init__(self, uuid, s_cur, s_nxt, flags, msg):
		self.uuid  = uuid
		self.s_cur = s_cur
		self.s_nxt = s_nxt
		self.flags = flags
		self.msg = msg 
	
	def sanitized_msg(self):
		return self.msg 

	def __str__(self):
		return "<TransitionError(%r, %r) [%r]=>[%r]>" % (self.uuid, self.flags, self.s_cur, self.s_nxt)

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



class NoResourceFound(Exception):

	def __init__(self, r_type, r_id, msg=None, loc=None):
		self.rt = r_type
		self.id = r_id
		self.msg = msg
		self.loc = loc

	def __str__(self):
		return '<No%rFound::%r>' % (self.rt, self.id)



class NoOauthFound(Exception):
	def __init__(self, uid, otype):
		self.uid = uid 
		self.ot  = otype
		
	def __str__(self):
		return "Oauth (%s, %s) not found" % (self.uid, self.ot)


class NoProposalFound(Exception):
	def __init__(self, p_uuid, p_from):
		self.prop_uuid = p_uuid
		self.prop_from = p_from
		
	def __str__(self):
		return "Proposal (%s, %s) not found" % (self.prop_uuid, self.prop_from)


class NoProfileFound(Exception):
	def __init__(self, pid, msg):
		self.puid = pid 
		self.msg  = msg
		
	def __str__(self):
		return "Profile %s not found, %s" % (self.puid, self.msg)

class NoReviewFound(Exception):
	def __init__(self, rid, msg):
		self.ruid = rid 
		self.msg  = msg
		
	def __str__(self):
		return "Review (%s, %s) not found" % (self.ruid, self.msg)


class ReviewError(Exception):
	def __init__(self, op, exp, seen, msg):
		self.op = op
		self.exp = exp
		self.seen = seen
		self.msg = msg

	def __str__(self):
		return "Review error during %s.  Exp[%s/%s]" % (self.op, self.exp, self.seen)



class InvalidCreditCard(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
