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
from flask import render_template, make_response, redirect
from flask import session, request, jsonify
from sqlalchemy.exc		import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from datetime import datetime as dt



MESSAGE = { '(IntegrityError) duplicate key value violates unique constraint "ix_account_email' : 'Email is already in use', }


class ApiError(object):
	# see example in routes/auth/password
	def __init__(self, status='An issue occurred', errors=[]):
		self.status = status
		self.errors = errors

	@property
	def serialize(self):
		return jsonify ({ 'status': self.status, 'errors': self.errors })





class SanitizedException(Exception):
	def __init__(self, exception, status='An issue occurred', errors=[], code=400):
		self.__exception = exception
		self.__next = None
		self.__code = code

		self.__reason = None		# extra context, truth
		self.__status = status		# user friendly message
		self.__errors = errors


	def exception(self):	  return	 (self.__exception)
	def exception_type(self): return type(self.__exception)

	def code(self, update_code = None):
		if (update_code): self.__code = update_code
		return self.__code

	def next(self, update_next = None):
		if (update_next): self.__next = update_next
		return self.__next

	def status(self, update_status = None):
		if (update_status): self.__status = update_status
		return self.__status

	def errors(self, update_errors = None):
		if (update_errors): self.__errors = update_errors
		return self.__errors

#	not working
#	def append_error(self, key, value):
#		self.__errors.append({ key : value })

	def reason(self, update_msg = None):
		if (update_msg): self.__reason = update_msg
		return self.__reason


	def response(self):
		# allow route/errors to catch and render HTML page
		#if (method == 'GET'): raise self	-- ?

		# POSTed from Web-Client, respond with JSON Error Mesg.
		print 'response = POST : code(' + str(self.__code) + ') : ' + str(self.__status) + ' : ' + str(self.__errors)
		api_resp = jsonify ({ 'status': self.__status, 'errors': self.__errors })
		return make_response(api_resp, self.__code)


	@staticmethod
	def sanitize_message(error_msg):
		print 'sanitize "' + error_msg[0:81] + '"'
		rc = MESSAGE.get(error_msg[0:81], error_msg)
		print rc
		return rc


################################################################################
### SUBCLASS EXCEPTIONS ########################################################
################################################################################


class InvalidInput(SanitizedException):
	def __init__(self, status=None, errors=None):
		SanitizedException.__init__(self, 'Invalid Input', status, errors)
		print self.exception()

	def __str__(self): return '<InvalidInput:%r:%r:%r>' % (self.status(), self.errors(), self.code())



class AccountError(SanitizedException):
	def __init__(self, email, status=None):
		SanitizedException.__init__(self, status='Account Creation Failed')
		self.email = email
	def __str__(self): return '<AccountError:%r:%r>' % (self.email, self.reason())



class PasswordError(SanitizedException):
	def __init__(self, account_id, status='Password does not match what is on file.', errors=[]):
		SanitizedException.__init__(self, 'Password Error', status=status, errors=errors, code=401)
		self.account = account_id

	def __str__(self): return '<Passworderror:%r:%r>' % (self.account, self.reason())



class StateTransitionError(SanitizedException):
	def __init__(self, resrc, resrc_id, state_cur, state_nxt, flags=None, user_msg=None):
		#print 'StateTransitionError()\tcreating'
		super(StateTransitionError, self).__init__(None, user_msg=user_msg)
		self.resrc		= str(resrc)
		self.resrc_id	= resrc_id
		self.state_cur	= state_cur
		self.state_nxt	= state_nxt
		self.flags	= flags
		self.reason(str(resrc) + ' ' + resrc_id + ' cannot transition to STATE(' + str(state_nxt) + '): ' + str(user_msg))
		#print 'StateTransitionError()\tcompleting'

	def __str__(self):
		return "<TransitionError(%r, %r) => %r>" % (self.resrc_id, self.state_cur, self.state_nxt)




class NoResourceFound(SanitizedException):
	def __init__(self, resrc, resrc_id):
		status = resrc + ' \'' + resrc_id + '\' not found'
		SanitizedException.__init__(self, 'Resource Error', status=status)
		self.resrc		= str(resrc)
		self.resrc_id	= str(resrc_id)

	def __str__(self): return '<NoResourceFound:%r:%r>' % (self.resrc, self.resrc_id)



class NoReferralFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Referral', str(rid))

class NoAccountFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Account', str(rid))

class NoProfileFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Profile', str(rid))

class NoReviewFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Review', str(rid))

class NoEmailFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Email', str(rid))

class NoOauthFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Oauth', str(rid))

class NoGiftFound(NoResourceFound):
	def __init__(self, rid): NoResourceFound('Gift', str(rid))



class ReviewError(SanitizedException):
	def __init__(self, op, exp, seen, user_msg=None):
		super(ReviewError, self).__init__(None, status=user_msg)
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

