from flask import render_template
from . import insprite_views




def create_error_response(resp_code, resp_text, resp_template):
	# when a request originates from an API client, return an API type-of response (json).
	if (request.accept_mimetypes.accept_json and not request.accept_mimetpes.accept_html):
		json_resp = jsonify({'error' : resp_text})
		json_resp.status_code = resp_code
		return json_resp
	return render_template(resp_template), resp_code




@insprite_views.app_errorhandler(400)
def error_400_bad_request(e):
	print 'Error, returning 400 response. The request was invalid or inconsistent (with our expectations).'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 400 template.\n\n'
	return render_template('404.html'), 400




@insprite_views.app_errorhandler(401)
def error_401_unauthorized(e):
	print 'Error, returning 401 response. The request lacks authentication.'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 401 template.\n\n'
	return render_template('404.html'), 401




@insprite_views.app_errorhandler(403)
def error_403_forbidden(e):
	print 'Error, returning 403 response. The request was forbidden (even with current authentication level).'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 403 template.\n\n'
	return render_template('404.html'), 403




@insprite_views.app_errorhandler(404)
def error_404_not_found(e):
	print 'Error, returning 404 response. The resource requested was not found.'
	return render_template('404.html'), 404




@insprite_views.app_errorhandler(405)
def error_405_method_not_allowed(e):
	print 'Error, returning 405 response. The requested method (GET, POST, HEAD, etC) is not supported for the given resource.'
	print 'Missing Template.  returning. 404 template instead.\n\nTODO: create 405 template.\n\n'

	if (request.accept_mimetypes.accept_json and not request.accept_mimetpes.accept_html):
		json_resp = jsonify({'error' : 'method not allowed'})
		json_resp.status_code = 405
		return json_resp
	return render_template('404.html'), 405




@insprite_views.app_errorhandler(500)
def error_500_internal_server_error(e):
	print 'Error, returning 500 response. An unexpected server error occurred while processing request.'
	return create_error_response(500, 'Internal server error', '500.html')
