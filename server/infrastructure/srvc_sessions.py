#################################################################################
# Copyright (C) 2014 HeroTime, Inc.
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

import pickle
import time, uuid
import OpenSSL, hashlib, base64
from datetime import timedelta
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from flask_redis import Redis
from werkzeug.datastructures import CallbackDict


class RedisSession(CallbackDict, SessionMixin):
	def __init__(self, initial=None, sid=None, new=False):
		def on_update(self):
			self.modified = True
		CallbackDict.__init__(self, initial, on_update)
		self.sid = sid
		self.new = new
		self.modified = False

	def __repr__(self):
		return '<redis-session %r, %r, %r>' % (self.sid, self.new, self.modified)
	
	def get_sid(self):
		return self.sid
	



class RedisSessionInterface(SessionInterface):
	serializer = pickle
	session_class = RedisSession

	def __init__(self, redis=None, prefix='session:'):
		# print('initializing sessions')
		if redis is None:
			redis = Redis()

		self.redis  = redis
		self.prefix = prefix


	def generate_sid(self):
		return hashlib.md5(repr(time.time())).hexdigest()


	def get_redis_expiration_time(self, ht_srv, session):
		if session.permanent:
			return ht_srv.permanent_session_lifetime
		return timedelta(days=1)


	def open_session(self, ht_srv, request):
		""" Creates new session_class object(RedisSession) each time. """
		sid = request.cookies.get(ht_srv.session_cookie_name)
		if not sid:
			# create a _new_ session, with a new session identifier
			return self.session_class(sid=self.generate_sid(), new=True)

		# get user's current session with 'sid' 
		val = self.redis.get(self.prefix + sid)
		if val is not None:
			data = self.serializer.loads(val)
			return self.session_class(data, sid=sid)

		return self.session_class(sid=sid, new=True)


	def save_session(self, ht_srv, session, response):
		domain = self.get_cookie_domain(ht_srv)
		#print ('save session ' + str(session.get('sid')))
		#print "domain = ", domain
		#print "perm_sess_lifetime = ", ht_srv.permanent_session_lifetime

		if not session:
			self.redis.delete(self.prefix + session.sid)
			if session.modified:
				response.delete_cookie(ht_srv.session_cookie_name, domain=domain)
			return

		redis_exp  = self.get_redis_expiration_time(ht_srv, session)
		cookie_exp = self.get_expiration_time(ht_srv, session)
		val = self.serializer.dumps(dict(session))
		self.redis.setex(self.prefix + session.sid, val, int(self.total_seconds(redis_exp)))
		response.set_cookie(ht_srv.session_cookie_name, session.sid, expires=cookie_exp, httponly=True, domain=domain)

	def total_seconds(self, td):
		return td.days * 60 * 60 * 24 + td.seconds


