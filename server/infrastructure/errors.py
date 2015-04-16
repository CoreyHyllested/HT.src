#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


import sys, traceback
from flask import render_template, session, request, jsonify
from sqlalchemy.exc		import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from datetime import datetime as dt




class SanitizedException(Exception):
	def __init__(self, error, resp_code=400, user_msg=None):
		self._exception = error
		self._http_resp = resp_code
		self._http_next = None
		self._http_mesg = str(user_msg)			# show users a friendly message
		self._tech_mesg = str(error)		# preserve the truth
	
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

class AccountError(SanitizedException):
	def __init__(self, email, error='Account creation failed'):
		super(AccountError, self).__init__(error, resp_code=400)
		self.email = email
		self.sanitized_msg(msg = error)

	def __str__(self):
		return '<AccountError:%r:%r>' % (self.email, self._tech_mesg)


class PasswordError(SanitizedException):
	def __init__(self, account, error='Password does not match what is on file'):
		super(PasswordError, self).__init__(error, resp_code=401)
		self.account = account
		self.sanitized_msg(msg = error)

	def __str__(self):
		return '<Passworderror:%r:%r>' % (self.account, self._tech_mesg)



class StateTransitionError(SanitizedException):
	def __init__(self, resrc, resrc_id, state_cur, state_nxt, flags=None, user_msg=None):
		#print 'StateTransitionError()\tcreating'
		super(StateTransitionError, self).__init__(None, user_msg=user_msg)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.state_cur	= state_cur
		self.state_nxt	= state_nxt
		self.flags	= flags
		self.technical_msg(str(resrc) + ' ' + resrc_id + ' cannot transition to STATE(' + str(state_nxt) + '): ' + str(user_msg))
		#print 'StateTransitionError()\tcompleting'

	def __str__(self):
		return "<TransitionError(%r, %r) => %r>" % (self.resrc_id, self.state_cur, self.state_nxt)




class NoResourceFound(SanitizedException):
	def __init__(self, resrc, resrc_id, error_msg=None):
		super(NoResourceFound, self).__init__(None)
		self.resrc		= str(resrc)
		self.resrc_id	= str(resrc_id)
		self.sanitized_msg(self.resrc + ' \'' + self.resrc_id + '\' not found.')
		self.technical_msg(self.resrc + ' '   + self.resrc_id + ' not found.')

	def __str__(self):
		return '<NoResourceFound:%r:%r>' % (self.resrc, self.resrc_id)


class NoProposalFound(NoResourceFound):
	def __init__(self, pid): super(NoProposalFound, self).__init__('Proposal', str(pid))

class NoMeetingFound(NoResourceFound):
	def __init__(self, mid): super(NoMeetingFound, self).__init__('Meeting', str(mid))

class NoProfileFound(NoResourceFound):
	def __init__(self, pid): super(NoProfileFound, self).__init__('Profile', str(pid))

class NoReviewFound(NoResourceFound):
	def __init__(self, rid): super(NoReviewFound, self).__init__('Review', str(rid))

class NoOauthFound(NoResourceFound):
	def __init__(self, uid): super(NoOauthFound, self).__init__('Oauth', str(uid))

class NoGiftFound(NoResourceFound):
	def __init__(self, gid): super(NoGiftFound, self).__init__('Gift', str(gid))


#replace with NoGiftFound.
class GiftNotFoundError(SanitizedException):
	def __init__(self, gift_id, flags=None, user_msg=None):
		super(GiftNotFoundError, self).__init__(None, resp_code=400, user_msg=user_msg)
		self.gift_id = str(gift_id)
		self.flags	= flags
		self.technical_msg(str(gift_id) + ' ' + ' does not exist.  Already, consumed?')

	def __str__(self):
		return "<NoGiftFound (%r)>" % (self.gift_id)



class ReviewError(SanitizedException):
	def __init__(self, op, exp, seen, user_msg=None):
		super(ReviewError, self).__init__(None, user_msg=user_msg)
		self.op = op
		self.exp = exp
		self.seen = seen
		self.msg = msg

	def __str__(self):
		return "Review error during %s.  Exp[%s/%s]" % (self.op, self.exp, self.seen)




################################################################################
### EXCEPTION FUNCTIONS ########################################################
################################################################################

def ht_sanitize_error(error, details=None, reraise=True):
	print 'ht_sanitize_error()\t' + str(type(error)) + ' ' +  str(error)
	if ((type(error) == NoResourceFound) or
		(type(error) == StateTransitionError)):
		print 'Error Caught already a Sanitized Exception '
		e = error
	elif (type(error) == IntegrityError):
		e = SanitizedException(error, resp_code=400, user_msg="Database Failure")
	elif (type(error) == TypeError):
		e = SanitizedException(error, resp_code=500, user_msg="Server Error")
	elif (type(error) == NameError):
		e = SanitizedException(error, resp_code=500, user_msg="Server Error")
		print 'ht_sanitize_error() NAME ERROR\n', traceback.format_exc()
	elif (type(error) == ValueError):
		e = SanitizedException(error, resp_code=400, user_msg="Invalid input")
	else:
		print 'ht_sanitize_error()\tcreating SE from ' + str(type(error))
		e = SanitizedException(error, resp_code=400)

	if (reraise): raise e
	else:
		print 'ht_sanitize_error() traceback\n', traceback.format_exc()
		print 'ht_sanitize_error() exec_info\n', sys.exc_info()[0]


def dump_error(error):
	print 'dump_error() traceback\n', traceback.format_exc()
	print 'dump_error() exec_info\n', sys.exc_info()[0]

