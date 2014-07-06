#################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
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


import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_oauthlib.client	import OAuth
from flask.ext.compress		import Compress
from flask.ext.mail		import Mail
from flask_wtf.csrf		import CsrfProtect
from flask_redis		import Redis
from server.infrastructure.initialize_ht	import *
from server.infrastructure.srvc_sessions	import RedisSessionInterface
from config import server_configuration



log_frmtr = logging.Formatter('%(asctime)s %(levelname)s %(message)s')	#[in %(pathname)s:%(lineno)d]'))
log_hndlr = RotatingFileHandler('/tmp/ht.log', 'a', 1024*1024, 10) 
log_hndlr.setFormatter(log_frmtr)
log_hndlr.setLevel(logging.INFO)

create_dir('/tmp/ht_upload/')

def initialize_server(config_name):
	print 'initializing server'
	ht_server = Flask(__name__)
	ht_server.config.from_object(server_configuration['development'])
	ht_server.secret_key = '\xfai\x17^\xc1\x84U\x13\x1c\xaeU\xb1\xd5d\xe8:\x08\xf91\x19w\x843\xee'
	ht_server.debug = True
	ht_server.logger.setLevel(logging.DEBUG)
	ht_server.logger.addHandler(log_hndlr)	 #ht_server.logger.addHandler(logging.FileHandler("/tmp/ht.log", mode="a"))

	print 'configuring server'
	return ht_server

ht_server = initialize_server('')
application = ht_server


print 'initializing session mgmt'
redis_cache = Redis(ht_server)
ht_server.session_interface = RedisSessionInterface(redis=redis_cache)


Compress(ht_server)
ht_csrf  = CsrfProtect(ht_server)
ht_oauth = OAuth(ht_server)

facebook = ht_oauth.remote_app(
	'facebook',
	base_url='https://graph.facebook.com',
	request_token_url=None,
	access_token_url='/oauth/access_token',
	authorize_url='https://www.facebook.com/dialog/oauth',
	consumer_key=ht_server.config['FACEBOOK_APP_ID'],
	consumer_secret=ht_server.config['FACEBOOK_APP_SEC'],
	request_token_params={
		'scope': 'email'
	}
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


from server.infrastructure import srvc_database
from server import views, controllers 
from routes import authentication, everyone, users, api, errors
from routes import insprite_views as main_blueprint
ht_server.register_blueprint(main_blueprint)
