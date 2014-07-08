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
from flask.ext.assets	import Environment, Bundle
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
ht_csrf  = CsrfProtect()
ht_oauth = OAuth()

ht_server = None

def initialize_server(config_name):
	print 'initializing server'
	global ht_server
	ht_server = Flask(__name__)
	ht_server.config.from_object(server_configuration[config_name])
	ht_server.secret_key = '\xfai\x17^\xc1\x84U\x13\x1c\xaeU\xb1\xd5d\xe8:\x08\xf91\x19w\x843\xee'
	ht_server.debug = True
	ht_server.logger.setLevel(logging.DEBUG)
	ht_server.logger.addHandler(log_hndlr)	 #ht_server.logger.addHandler(logging.FileHandler("/tmp/ht.log", mode="a"))

	ht_csrf.init_app(ht_server)
	ht_oauth.init_app(ht_server)
	assets = Environment(ht_server)
	assets.url = ht_server.static_url_path


	jsfilter = ht_server.config['JSFILTER']
	# Note, Bundle looks for input files (e.g. 'js/format.js') and saves output files dir relative to '/static/'
	js_dashboard_maps_format = Bundle('js/maps.js', 'js/format.js', filters=jsfilter, output='js/maps.format.js')
	css_example = Bundle('scss/helper.sass', filters='pyscss', output='css/foo.css')

	assets.register('js_mapformat', js_dashboard_maps_format)
	assets.register('sass_foo', css_example)

	# print('initializing session mgmt')
	redis_cache = Redis(ht_server)
	ht_server.session_interface = RedisSessionInterface(redis=redis_cache)

	Compress(ht_server)

	from server.infrastructure import srvc_database
	from routes import authentication, everyone, users, api, errors, testing
	from routes import insprite_views as main_blueprint
	from routes import insprite_tests as test_blueprint
	ht_server.register_blueprint(main_blueprint)
	ht_server.register_blueprint(test_blueprint)


	return ht_server
