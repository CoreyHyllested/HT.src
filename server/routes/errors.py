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

from server.models import Profile
from server.routes import meta_routes as server_routes
from server.infrastructure.errors import *
from jinja2.exceptions import *




def create_error_response(resp_code, resp_text, resp_template):
	# when a request originates from an API client, return an API type-of response (json).
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))

	if (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html):
		json_resp = jsonify({'error' : resp_text})
		json_resp.status_code = resp_code
		return json_resp
	return render_template(resp_template, bp=profile), resp_code




@server_routes.app_errorhandler(StateTransitionError)
def error_400_bad_request_ste(ste):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 400 response. The request was invalid, asking for an invalid state transition change.'
	print 'bad_request_ste sanitized', ste.status()
	print 'bad_request_ste technical', str(ste.exception())

	# log the resource.
	# log the transition error.
	# log the account / user / profile_id -- can only come from user with account.
	return render_template('404.html', bp=profile), 400




@server_routes.app_errorhandler(NoResourceFound)
def error_400_no_resource_found(nrf):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 400 response. The request was invalid, asking for an resource that could not be found.'
	print 'bad_resource_requested', nrf.status()
	print 'bad_resource_requested', str(nrf.exception())

	# log the resource.
	# log the account / user / profile_id -- can only come from user with account.
	return render_template('404.html', bp=profile), 400




@server_routes.app_errorhandler(400)
def error_400_bad_request(e):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 400 response. The request was invalid or inconsistent (with our expectations).'
	return render_template('404.html', bp=profile), 400




@server_routes.app_errorhandler(401)
def error_401_unauthorized(e):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 401 response. The request lacks authentication.'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 401 template.\n\n'
	return render_template('404.html', bp=profile), 401




@server_routes.app_errorhandler(403)
def error_403_forbidden(e):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 403 response. The request was forbidden (even with current authentication level).'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 403 template.\n\n'
	return render_template('404.html', bp=profile), 403




@server_routes.app_errorhandler(404)
def error_404_not_found(e):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 404 response. The resource requested was not found.'
	return render_template('404.html', bp=profile), 404




@server_routes.app_errorhandler(405)
def error_405_method_not_allowed(e):
	profile = None
	if 'uid' in session:
		profile = Profile.get_by_uid(session.get('uid'))
	print 'Error, returning 405 response. The requested method (GET, POST, HEAD, etC) is not supported for the given resource.'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 405 template.\n\n'

	if (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html):
		json_resp = jsonify({'error' : 'method not allowed'})
		json_resp.status_code = 405
		return json_resp
	return render_template('404.html', bp=profile), 405




@server_routes.app_errorhandler(SanitizedException)
def generic_error_sanitizedexception_error(e):
	print 'Error, returning 500 response. An unexpected server error occurred while processing request.'
	return create_error_response(500, 'Internal server error', '500.html')


@server_routes.app_errorhandler(IOError)
@server_routes.app_errorhandler(TemplateNotFound)
def no_template_error(e):
	print 'Returning 500 response. An unexpected server error occurred while processing request.'
	print 'Error:', str(e)
	return create_error_response(500, 'Internal server error', '500.html')


@server_routes.app_errorhandler(500)
def error_500_internal_server_error(e):
	print 'Error, returning 500 response. An unexpected server error occurred while processing request.'
	return create_error_response(500, 'Internal server error', '500.html')
