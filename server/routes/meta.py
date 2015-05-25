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


from . import sc_meta
from flask import render_template
from ..forms import ReviewForm
from .helpers import *
from server.controllers import *
from server.sc_utils import *


@sc_meta.route('/robots.txt')
@sc_meta.route('/humans.txt')
@sc_meta.route('/sitemap.xml')
def meta_serve_from_root():
	server_root_dir = sc_server.static_folder + '/root/'
	print server_root_dir
	return send_from_directory(server_root_dir, request.path[1:])



#  FOR MORE INFO.
#	http://flask.pocoo.org/docs/0.10/api/#flask.after_this_request
#	http://flask.pocoo.org/docs/0.10/api/#flask.send_file (kwargs)
#	Not using x-sendfile (we need the HTTPD module mod_xsendfile)...
#   http://makandracards.com/makandra/990-speed-up-file-downloads-with-rails-apache-and-x-sendfile
#	Other potentioal solution: https://github.com/corydolphin/flask-headers
@sc_meta.route('/static/img/<image>')
def meta_serve_static_img(image):
	@after_this_request
	def add_header(response):
		#print dir(response.cache_control)
		response.cache_control.max_age=5184000
		return response
	server_root_dir = sc_server.static_folder + '/img/'
	return send_from_directory(server_root_dir, str(image))



@sc_meta.route('/about/version', methods=['GET', 'POST'])
def meta_about_version():
	return make_response(render_template('version'))


