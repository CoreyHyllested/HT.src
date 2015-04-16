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


import os, logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from flask import Flask
from flask_oauthlib.client	import OAuth
from flask.ext.compress		import Compress
from flask.ext.assets	import Environment, Bundle
from flask.ext.mail		import Mail
from flask_wtf.csrf		import CsrfProtect
from flask_redis		import Redis
from server.infrastructure.srvc_sessions	import RedisSessionInterface
from server.infrastructure.srvc_database	import initialize_database
from config import server_configuration



log_frmtr = logging.Formatter('%(asctime)s %(levelname)s %(message)s')	#[in %(pathname)s:%(lineno)d]'))
log_hndlr = StreamHandler() #logs to stderr? #RotatingFileHandler('/tmp/ht.log', 'a', 1024*1024, 10) 
log_hndlr.setFormatter(log_frmtr)
log_hndlr.setLevel(logging.INFO)

ht_csrf  = CsrfProtect()
sc_csrf	= ht_csrf
ht_oauth = OAuth()
sc_oauth = ht_oauth

ht_server = None
sc_server = None

def create_upload_directory(sc_server):
	try:
		dir_upload = sc_server.config['HT_UPLOAD_DIR']
		os.makedirs(dir_upload)
	except OSError as oe:
		if (oe.errno != 17):
			print oe
			raise oe
	except Exception as e:
		print type(e), e
		raise e


def initialize_server(config_name):
	global sc_server, ht_server
	sc_server = Flask(__name__)
	ht_server = sc_server # dont break everything yet

	sc_server.config.from_object(server_configuration[config_name])
	if (config_name == 'production' or config_name == 'devel_money'):
		print 'using configuration... ', config_name

	sc_server.secret_key = '\xfai\x17^\xc1\x84U\x13\x1c\xaeU\xb1\xd5d\xe8:\x08\xf91\x19w\x843\xee'
	sc_server.debug = True
	sc_server.logger.setLevel(logging.DEBUG)
	sc_server.logger.addHandler(log_hndlr)	 #sc_server.logger.addHandler(logging.FileHandler("/tmp/ht.log", mode="a"))
	create_upload_directory(sc_server)

	redis_cache = Redis(sc_server)
	sc_server.session_interface = RedisSessionInterface(redis=redis_cache)
	initialize_database(sc_server.config)

	sc_csrf.init_app(sc_server)
	sc_oauth.init_app(sc_server)

	jsfilter = sc_server.config['JSFILTER']
	# Note, Bundle looks for input files (e.g. 'js/format.js') and saves output files dir relative to '/static/'
	js_dashboard_maps_format = Bundle('js/maps.js', 'js/format.js', filters=jsfilter, output='js/maps.format.js')
	css_schedule = Bundle('scss/schedule.scss', filters='pyscss', output='css/schedule.css')
	css_settings = Bundle('scss/settings.scss', filters='pyscss', output='css/settings.css')
	css_projects = Bundle('scss/projects.scss', filters='pyscss', output='css/projects.css')
	css_recovery = Bundle('scss/recovery.scss', filters='pyscss', output='css/recovery.css')

	assets = Environment(sc_server)
	assets.url = sc_server.static_url_path
	assets.register('js_mapformat', js_dashboard_maps_format)
	assets.register('sass_schedule', css_schedule)
	assets.register('scss_settings', css_settings)
	assets.register('scss_projects', css_projects)
	assets.register('scss_recovery', css_recovery)

	Compress(sc_server)

	from routes import authentication, everyone, users, api, errors, testing
	from routes import sc_users as sc_allusers
	from routes import sc_ebody as sc_everyone
	sc_server.register_blueprint(sc_everyone)
	sc_server.register_blueprint(sc_allusers)
	return sc_server

