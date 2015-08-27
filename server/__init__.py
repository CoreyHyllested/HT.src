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
from flask import Flask, make_response, jsonify
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
	server.trusted_index = None
	assets = Environment(server)
	assets.url = server.static_url_path
	assets.load_path.append(assets.directory + '/assets/scss')
	assets.load_path.append(assets.directory + '/assets/js')

	server_init_assets_css(assets)
	server_init_assets_js(server, assets)



def server_init_assets_css(assets):
	page_homepage =	Bundle('page_homepage.scss', filters='pyscss', output='css/homepage.css')
	page_about_sc =	Bundle('page_about_sc.scss', filters='pyscss', output='css/about-sc.css')
	page_products =	Bundle('page_products.scss', filters='pyscss', output='css/products.css')
	page_settings =	Bundle('page_settings.scss', filters='pyscss', output='css/settings.css')
	theme_master =	Bundle('master.scss',		filters='pyscss', output='css/the-master.css')
	theme_legal =	Bundle('theme_legal.scss',	filters='pyscss', output='css/legaltos.css')
	theme_error	=	Bundle('theme_error.scss',	filters='pyscss', output='css/errors.css')
	theme_login = Bundle('theme_authorize.scss', filters='pyscss', output='css/authorize.css')
	theme_dashboard = Bundle('theme_dashboard.scss', filters='pyscss', output='css/dashboards.css')
	theme_referral = Bundle('theme_referral.scss', filters='pyscss', output='css/referral.css')
	theme_profiles = Bundle('profiles.scss', filters='pyscss', output='css/profiles.css')
	theme_projects = Bundle('theme_projects.scss', filters='pyscss', output='css/projects.css')


	assets.register('scss_landpage', page_homepage)
	assets.register('scss_about_sc', page_about_sc)
	assets.register('scss_products', page_products)
	assets.register('scss_settings', page_settings)
	assets.register('master', 		 theme_master)
	assets.register('scss_loginsys', theme_login)
	assets.register('scss_legaltos', theme_legal)
	assets.register('scss_errors',	 theme_error)
	assets.register('scss_referral', theme_referral)
	assets.register('scss_profiles', theme_profiles)
	assets.register('scss_projects', theme_projects)
	assets.register('scss_dashboard', theme_dashboard)




def server_init_assets_js(server, assets):
	jsfilter = server.config['JSFILTER']

	# Bundle looks for input files (e.g. 'js/format.js') and saves output files dir relative to /static/
	js_common	= Bundle('modals.js', 'feedback.js', filters=jsfilter, output='js/common.js')
	js_projects = Bundle('projects.js', 'maps.js', filters=jsfilter, output='js/projects.js')
	js_referral	= Bundle('referral.js', 'maps.js', filters=jsfilter, output='js/referral.js')
	js_profiles	= Bundle('profiles.js', 'plugins/scrollto.jq', filters=jsfilter, output='js/profiles.js')
	js_settings	= Bundle('settings.js', filters=jsfilter, output='js/settings.js')
	js_dashboard = Bundle('dashboard.js', filters=jsfilter, output='js/dashboard.js')

	assets.register('js_dashboard', js_dashboard)
	assets.register('js_common',	js_common)
	assets.register('js_profiles',	js_profiles)
	assets.register('js_projects',	js_projects)
	assets.register('js_referral',	js_referral)
	assets.register('js_settings',	js_settings)



def server_init_routes(server):
	Compress(sc_server)
	server.csrf	= CsrfProtect()
	server.csrf.init_app(server)

	@server.csrf.error_handler
	def _csrf_error(reason):
		return make_response(jsonify(csrf=reason), 400)

	from routes.api import list, project, referral
	from routes.authenticate import password
	from routes.authenticate import facebook, stripe
	from routes import everyone, users, meta, errors
	from routes import public_routes
	from routes import auth_routes
	from routes import meta_routes
	from routes import api_routing
	server.register_blueprint(public_routes)
	server.register_blueprint(auth_routes)
	server.register_blueprint(meta_routes)
	server.register_blueprint(api_routing)

