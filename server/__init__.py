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
from flask.ext.sqlalchemy	import SQLAlchemy
from flask.ext.assets	import Environment, Bundle
from flask_wtf.csrf		import CsrfProtect
from flask_redis		import Redis
from server.infrastructure.srvc_sessions	import RedisSessionInterface
from server.infrastructure.srvc_database	import initialize_database
from config import server_configuration


sc_server	= None
database	= None


def initialize_server(config_name):
	global sc_server
	sc_server = Flask(__name__)

	server_init_environment(sc_server, config_name)
	server_init_logging(sc_server)

	server_init_service_database(sc_server)
	server_init_service_sessions(sc_server)
	server_init_service_oauth(sc_server)

	server_init_assets(sc_server)
	server_init_routes(sc_server)
	return sc_server



def	server_init_environment(server, configuration):
	server.secret_key = '\xfai\x17^\xc1\x84U\x13\x1c\xaeU\xb1\xd5d\xe8:\x08\xf91\x19w\x843\xee'
	server.config.from_object(server_configuration[configuration])
	if (configuration == 'production' or configuration == 'devel_money'):
		print 'using configuration... ', configuration
#	server.use_x_sendfile = server.config.get('USE_SENDFILE', False)	mod_xsendfile not installed on AWS/httpd

	try:
		# create upload directory.
		dir_upload = server.config['SC_UPLOAD_DIR']
		os.makedirs(dir_upload)
	except OSError as oe:
		if (oe.errno != 17):
			print oe
			raise oe
	except Exception as e:
		print type(e), e
		raise e


def	server_init_logging(server):
	log_frmtr = logging.Formatter('%(asctime)s %(levelname)s %(message)s')	#[in %(pathname)s:%(lineno)d]'))
	log_hndlr = StreamHandler() #logs to stderr? #RotatingFileHandler('/tmp/ht.log', 'a', 1024*1024, 10) 
	log_hndlr.setFormatter(log_frmtr)
	log_hndlr.setLevel(logging.INFO)

	server.debug = True
	server.logger.setLevel(logging.DEBUG)
	server.logger.addHandler(log_hndlr)	 #sc_server.logger.addHandler(logging.FileHandler("/tmp/ht.log", mode="a"))
	


def server_init_service_sessions(server):
	redis_cache = Redis(server)
	server.session_interface = RedisSessionInterface(redis=redis_cache)



def server_init_service_database(server):
	global database		# import database

#	if (database and database.session):
#		print 'reset database session'
#		database.session.remove()

	server.database = SQLAlchemy(server)
	database = server.database
	from server import models
	#initialize_database(server.config)



def server_init_service_oauth(server):
	server.oauth = OAuth()
	server.oauth.init_app(sc_server)



def	server_init_assets(server):
	jsfilter = server.config['JSFILTER']

	# Note, Bundle looks for input files (e.g. 'js/format.js') and saves output files dir relative to '/static/'
	js_dashboard_maps_format = Bundle('js/maps.js', 'js/format.js', filters=jsfilter, output='js/maps.format.js')
	css_loginsys =	Bundle('scss/authorize.scss', filters='pyscss', output='css/authorize.css')
	css_errors	=	Bundle('scss/errors.scss', filters='pyscss', output='css/errors.css')
	css_about_sc =	Bundle('scss/about-sc.scss', filters='pyscss', output='css/about-sc.css')
	css_landpage =	Bundle('scss/landpage.scss', filters='pyscss', output='css/landpage.css')
	css_legaltos =	Bundle('scss/legaltos.scss', filters='pyscss', output='css/legaltos.css')
	css_products =	Bundle('scss/products.scss', filters='pyscss', output='css/products.css')
	css_projects =	Bundle('scss/projects.scss', filters='pyscss', output='css/projects.css')
	css_recovery =	Bundle('scss/recovery.scss', filters='pyscss', output='css/recovery.css')
	#css_schedule =	Bundle('scss/schedule.scss', filters='pyscss', output='css/schedule.css')
	css_settings =	Bundle('scss/settings.scss', filters='pyscss', output='css/settings.css')
	css_dashboard = Bundle('scss/dashboard.scss', filters='pyscss', output='css/pro_dashboard.css')
	elem_header	=	Bundle('scss/elem-navigate.scss', 'scss/modals.scss', filters='pyscss', output='css/navigate.css')

	assets = Environment(server)
	assets.url = server.static_url_path
	assets.register('js_mapformat', js_dashboard_maps_format)
	assets.register('scss_about_sc', css_about_sc)
	assets.register('scss_errors',	css_errors)
	assets.register('scss_landpage', css_landpage)
	assets.register('scss_legaltos', css_legaltos)
	assets.register('scss_loginsys', css_loginsys)
	assets.register('scss_recovery', css_recovery)
	assets.register('scss_products', css_products)
	assets.register('scss_projects', css_projects)
	#assets.register('scss_schedule', css_schedule)
	assets.register('scss_settings', css_settings)
	assets.register('scss_dashboard', css_dashboard)
	assets.register('navigate.css', elem_header)



def server_init_routes(server):
	server.csrf	= CsrfProtect()
	server.csrf.init_app(server)
	Compress(sc_server)

	from routes.api import referral, list
	from routes import authentication, everyone, users, meta, errors
	from routes import api_routing
	from routes import meta_routes
	from routes import sc_users as sc_allusers
	from routes import sc_ebody as sc_everyone
	server.register_blueprint(sc_everyone)
	server.register_blueprint(sc_allusers)
	server.register_blueprint(meta_routes)
	server.register_blueprint(api_routing)
