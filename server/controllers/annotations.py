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


import logging, functools, urllib
from server import sc_server
from flask import *


def trace(msg):
	sc_server.logger.info(msg)

def sc_debug(msg):
	if sc_server.debug: print(msg)

def ht_debug(msg):
	#if sc_server.debug: sc_server.logger.info(msg)
	sc_debug(msg)

def log_uevent(uid, msg):
	sc_server.logger.info(str(uid) + " " + str(msg))


################################################################################
### ANNOTATIONS ################################################################
################################################################################

def sc_authenticated(function):
	@functools.wraps(function)
	def verify_authenticated_user(*args, **kwargs):
		if 'uid' not in session:
			target = request.referrer
			if target and request.method == 'POST':
				session['redirect'] = "%s?%s" % (target, urllib.urlencode(request.form))
				session['messages'] = "That operation requires you to login first."
				return make_response(jsonify(next=session['redirect']), 401)
			return make_response(redirect('/login'))

		return function(*args, **kwargs)
	return verify_authenticated_user



def sc_administrator(function):
	@functools.wraps(function)
	def verify_authenticated_admin(*args, **kwargs):
		if 'uid' not in session:
			trace("no uid; " + function.__name__ + ': redirect to login')
			return make_response(redirect('/login'))
		if 'admin' not in session:
			trace("no uid; " + function.__name__ + ': return 400')
			raise Exception('Missing authenication')
		return function(*args, **kwargs)
	return verify_authenticated_admin



def deprecated(function):
	@functools.wraps(function)
	def print_deprecated(*args, **kwargs):
		print '**DEPRECATED** ' + str(function.__name__)
		return function(*args, **kwargs)
	return print_deprecated



def dbg_enterexit(orig_fn):
	@functools.wraps(orig_fn)
	def logged_fn(*args, **kwargs):
		uid = session.get('uid')
		sc_debug(orig_fn.__name__ + ': enter ' + str(uid))
		rc = orig_fn(*args, **kwargs)
		sc_debug(orig_fn.__name__ + ': rc = ' + str(rc))
		return rc
	return logged_fn

