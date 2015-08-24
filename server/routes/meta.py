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


from server.routes import meta_routes as meta
from server.routes import helpers
from server.controllers import *


<<<<<<< HEAD
@sc_meta.route('/projects.json')
@sc_meta.route('/robots.txt')
@sc_meta.route('/humans.txt')
@sc_meta.route('/sitemap.xml')
def meta_serve_from_root():
	server_root_dir = sc_server.static_folder + '/root/'
	#if (debug): print server_root_dir
=======
@meta.route('/google5feb31e1e5dc741b.html')
@meta.route('/robots.txt')
@meta.route('/humans.txt')
@meta.route('/sitemap.xml')
@meta.route('/context.json')
def meta_serve_from_root():
	server_root_dir = sc_server.static_folder + '/root/'
>>>>>>> master
	return send_from_directory(server_root_dir, request.path[1:])


#  FOR MORE INFO.
#	http://flask.pocoo.org/docs/0.10/api/#flask.after_this_request
#	http://flask.pocoo.org/docs/0.10/api/#flask.send_file (kwargs)
#	Not using x-sendfile (we need the HTTPD module mod_xsendfile)...
#   http://makandracards.com/makandra/990-speed-up-file-downloads-with-rails-apache-and-x-sendfile
#	Other potentioal solution: https://github.com/corydolphin/flask-headers
@meta.route('/static/img/<image>')
def meta_serve_static_img(image):
	@after_this_request
	def add_header(response):
		#print dir(response.cache_control)
		response.cache_control.max_age=5184000
		return response
	server_root_dir = sc_server.static_folder + '/img/'
	return send_from_directory(server_root_dir, str(image))


@meta.route('/about/version', methods=['GET', 'POST'])
def meta_about_version():
	return make_response(render_template('version'))

