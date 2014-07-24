#################################################################################
# Copyright (C) 2014 Insprite, LLC.
# All Rights Reserved.
#
# All information contained is the property of Insprite, LLC.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Insprite, LLC.
#################################################################################


import sys
from flask import render_template, session, request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime as dt




class SanitizedException(Exception):
	def __init__(self, error, resp_code=400, msg=None):
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
		print 'api_response = POST : resp(' + str(self._http_resp) + ') : ' + str(self._http_mesg)
		return jsonify(usrmsg=self._http_mesg), self._http_resp




################################################################################
### SUBCLASS EXCEPTIONS ########################################################
################################################################################


class StateTransitionError(SanitizedException):
	def __init__(self, resrc, resrc_id, state_cur, state_nxt, flags=None, error_msg=None):
		#print 'StateTransitionError()\tcreating'
		super(StateTransitionError, self).__init__(None, msg=error_msg)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.state_cur	= state_cur
		self.state_nxt	= state_nxt
		self.flags	= flags
		self.technical_msg(str(resrc) + ' ' + resrc_id + ' cannot transition to STATE(' + str(state_nxt) + '): ' + str(error_msg))
		#print 'StateTransitionError()\tcompleting'

	def __str__(self):
		return "<TransitionError(%r, %r) => %r>" % (self.resrc_id, self.state_cur, self.state_nxt)




class NoResourceFound(SanitizedException):
	def __init__(self, resrc, resrc_id, error_msg=None):
		super(NoResourceFound, self).__init__(None)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.sanitized_msg(str(resrc) + ' ' + resrc_id + ' not found.')
		self.technical_msg(str(resrc) + ' ' + resrc_id + ' not found.')

	def __str__(self):
		return '<NoResourceFound:%r:%r>' % (self.resrc, self.resrc_id)


class NoProposalFound(NoResourceFound):
	def __init__(self, pid): super(NoProposalFound, self).__init__('Proposal', pid)

class NoMeetingFound(NoResourceFound):
	def __init__(self, mid): super(NoProposalFound, self).__init__('Meeting', mid)

class NoProfileFound(NoResourceFound):
	def __init__(self, pid): super(NoProfileFound, self).__init__('Profile', pid)
		
class NoReviewFound(NoResourceFound):
	def __init__(self, rid): super(NoReviewFound, self).__init__('Review', rid)



class ReviewError(SanitizedException):
	def __init__(self, op, exp, seen, error_msg=None):
		super(ReviewError, self).__init__(None, msg=error_msg)
		self.op = op
		self.exp = exp
		self.seen = seen
		self.msg = msg

	def __str__(self):
		return "Review error during %s.  Exp[%s/%s]" % (self.op, self.exp, self.seen)




################################################################################
### EXCEPTION FUNCTIONSl #######################################################
################################################################################

def ht_sanitize_error(error, details=None, reraise=True):
	print 'ht_sanitize_error()\t' + str(type(error)) + ' ' +  str(error)
	if ((type(error) == NoResourceFound) or
		(type(error) == StateTransitionError)):
		print 'PRE-Sanitized Exception '
		e = error
	elif (type(error) == ValueError):
		e = SanitizedException(error, resp_code=400, msg="Invalid input")
	else:
		e = SanitizedException(error, resp_code=400, msg=str(error))

	if (reraise): raise e

