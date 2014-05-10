#################################################################################
# Copyright (C) 2013 - 2014 HeroTime, Inc.
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
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_oauthlib.client	import OAuth
from flask.ext.compress		import Compress
from flask.ext.mail			import Mail
from flask_wtf.csrf			import CsrfProtect
from flask_redis			import Redis   
from server.infrastructure.srvc_sessions	import RedisSessionInterface


log_frmtr = logging.Formatter('%(asctime)s %(levelname)s %(message)s')	#[in %(pathname)s:%(lineno)d]'))
log_hndlr = RotatingFileHandler('/tmp/ht.log', 'a', 1024*1024, 10) 
log_hndlr.setFormatter(log_frmtr)
log_hndlr.setLevel(logging.INFO)

ht_server = Flask(__name__)
ht_server.secret_key = '\xfai\x17^\xc1\x84U\x13\x1c\xaeU\xb1\xd5d\xe8:\x08\xf91\x19w\x843\xee'
ht_server.config.from_object('config')
ht_server.debug = True
ht_server.logger.setLevel(logging.DEBUG)
ht_server.logger.addHandler(log_hndlr)	 #ht_server.logger.addHandler(logging.FileHandler("/tmp/ht.log", mode="a"))
application = ht_server


# use redis to perform user-session manangement
redis_cache = Redis(ht_server)
ht_server.session_interface = RedisSessionInterface(redis=redis_cache)


# configure postgresql -- dropped flask-sqlalchemy, more manual now.
#db.init_app(ht_server)
#db = SQLAlchemy(ht_server)
#db.create_all()
#engine = create_engine(ht_server.config['SQLALCHEMY_DATABASE_URI'])
#SM = sessionmaker(bind=engine)
#sq = SM()


# don't think we're using emailer
emailer = Mail(ht_server)
Compress(ht_server)
ht_csrf  = CsrfProtect(ht_server)
ht_oauth = OAuth(ht_server)




twitter = ht_oauth.remote_app(  'twitter',
								consumer_key=ht_server.config['TWITTER_KEY'],
								consumer_secret=ht_server.config['TWITTER_SEC'],
								request_token_params={ 'scope': 'r_basicprofile r_emailaddress', 'state': 'deadbeefcafe', },
								base_url='https://api.twitter.com/1/',
								access_token_method='POST',
								access_token_url='https://api.twitter.com/oauth/access_token',
								request_token_url='https://api.twitter.com/oauth/request_token',
								authorize_url='https://api.twitter.com/oauth/authorize',
							)

linkedin = ht_oauth.remote_app(  'linkedin',
								consumer_key=ht_server.config['LINKEDIN_KEY'],
								consumer_secret=ht_server.config['LINKEDIN_SEC'],
								request_token_params={ 'scope': 'r_basicprofile r_emailaddress', 'state': 'deadbeefcafe', },
								base_url='https://api.linkedin.com/v1/',
								request_token_url=None,
								access_token_method='POST',
								access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
								authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
							)

# must do this (approx.) last.
from server import views, controllers 
