import sys
from datetime import datetime as dt


class SanitizedException(Exception):
	def __init__(self, error, resp_code=400, msg=None):
		print 'SanitzedExeption()\t set exception to str() ' + str(error)
		self._exception = error
		self._http_resp = resp_code
		self._http_next = None
		self._http_mesg = None			# show users a friendly message
		self._tech_mesg = str(msg)		# preserve the truth
	
	def exception(self):
		return str(self._exception)

	def exception_type(self):
		return type(self._exception)

	def technical_msg(self, msg = None):
		if (msg is not None): self._tech_mesg = msg
		return self._tech_mesg

	def sanitized_msg(self, msg = None):
		if (msg is not None): self._http_mesg = msg
		return self._http_mesg

	def http_resp_code(self, rc = None):
		if (rc is not None): self._http_resp = rc
		return self._http_resp

	def http_next(self, nxt = None):
		if (nxt is not None): self._http_next = nxt
		return self._http_next
	
	def http_response(self, method):
		pass

	def api_response(self, method):
		# allow route/errors to catch and render HTML page
		if (method == 'GET'): raise self

		# POSTed from Web-Client, respond with JSON Error Mesg.
		return jsonify(usrmsg=self._http_mesg), self._http_resp






class StateTransitionError(SanitizedException):
	def __init__(self, resrc, resrc_id, state_cur, state_nxt, flags=None, error_msg=None):
		print 'StateTransitionError()\tcreating'
		super(StateTransitionError, self).__init__(None, msg=error_msg)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.state_cur	= state_cur
		self.state_nxt	= state_nxt
		self.flags	= flags
		self.technical_msg(str(resrc) + ' ' + resrc_id + ' cannot transition to STATE(' + str(state_nxt) + '): ' + error_msg)

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




class NoResourceFound(SanitizedException):
	def __init__(self, resrc, resrc_id, error_msg=None):
		super(NoResourceFound, self).__init__(None, msg=error_msg)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.technical_msg(str(resrc) + ' ' + resrc_id + ' not found.')

	def __str__(self):
		return '<NoResourceFound:%r:%r>' % (self.resrc, self.resrc_id)




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
