import sys
from datetime import datetime as dt


class SanitizedException(Exception):
	def __init__(self, error, httpRC=400, msg=None):
		self.exception = error
		self.next = None
		self.rc = httpRC

		if (msg is None):
			# ensure a message exists
			self.sanitized_msg = str(error)
	
	def exception(self):
		return str(self.exception)

	def exception_type(self):
		return type(self.exception)
	
	def sanitized_msg(self):
		return self.sanitized_msg
	
	def httpRC(self):
		return self.rc

	def httpNext(self):
		return self.sanitized_msg

	#def httpResp(self):
	#	return self.json




class StateTransitionError(SanitizedException):
#	def __init__(self, uuid, s_cur, s_nxt, flags=None, msg=None):
	def __init__(self, resrc, resrc_id, state_cur, state_nxt, flags=None, msg=None):
		super(StateTransitionError, self).__init__(None, msg=msg)
		self.resrc_id  = resrc_id
		self.state_cur = state_cur
		self.state_nxt = state_nxt
		self.flags = flags

	def update_msg(self, msg):
		self.sanitized_msg = msg

	def __str__(self):
		return "<TransitionError(%r, %r) => %r>" % (self.resrc_id, self.state_cur, self.state_nxt)




class DB_Error(Exception):
	def __init__(self, db_err, usr_msg):
		self.db_err  = db_err
		self.msg = usr_msg

	def sanitized_msg(self):
		return self.msg 

	def __str__(self):
		return "DB_ERR(%s, %s)" % (self.db_err, self.msg)



class PermissionDenied(Exception):
	def __init__(self, task, usr, usr_msg):
		self.task = task
		self.usr  = usr
		self.msg  = usr_msg

	def sanitized_msg(self):
		return self.msg 


	def __str__(self):
		return "PermissionError(%s, %s, %s)" % (self.task, self.usr, self.msg)



class NoResourceFound(Exception):

	def __init__(self, r_type, r_id, msg=None, loc=None):
		self.rt = r_type
		self.id = r_id
		self.msg = msg
		self.loc = loc

	def sanitized_msg(self):
		return self.msg 

	def __str__(self):
		return '<No%rFound::%r>' % (self.rt, self.id)



class NoOauthFound(Exception):
	def __init__(self, uid, otype, msg=None):
		self.uid = uid 
		self.ot  = otype
		self.msg = msg 
		
	def sanitized_msg(self):
		return self.msg 

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
