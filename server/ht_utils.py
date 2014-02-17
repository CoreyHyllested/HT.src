#################################################################################
# Copyright (C) 2012 - 2013 HeroTime, Inc.
# All Rights Reserved.
# 
# All information contained is the property of HeroTime, Inc.  Any intellectual 
# property about the design, implementation, processes, and interactions with 
# services may be protected by U.S. and Foreign Patents.  All intellectual 
# property contained within is covered by trade secret and copyright law.   
# 
# Dissemination or reproduction is strictly forbidden unless prior written 
# consent has been obtained from HeroTime, Inc.
#################################################################################


import logging
import functools
from server import ht_server
from flask import *


def trace(msg):
	ht_server.logger.info(msg)

def ht_debug(msg):
	if ht_server.debug: ht_server.logger.info(msg)

def log_uevent(uid, msg):
	ht_server.logger.info(str(uid) + " " + str(msg))
	


def dbg_enterexit(orig_fn):
	@functools.wraps(orig_fn)
	def logged_fn(*args, **kwargs):
		uid = session.get('uid')
		ht_debug(orig_fn.__name__ + ': enter ' + str(uid))
		rc = orig_fn(*args, **kwargs)
		ht_debug(orig_fn.__name__ + ': rc = ' + str(rc))
		return rc
	return logged_fn


def req_authentication(orig_fn):
	@functools.wraps(orig_fn)
	def verify_authenticated_user(*args, **kwargs):
		if 'uid' not in session:
			#flash('Must be logged in to view this page.', 'Error')
			trace("no uid; " + orig_fn.__name__ + ': redirect to login')
			return make_response(redirect('/login'))
		return orig_fn(*args, **kwargs)
	return verify_authenticated_user


