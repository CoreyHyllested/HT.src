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

from pprint import pprint as pp
from flask_oauthlib.client	import OAuth, OAuthException

from server.models import *
from server.routes import public_routes as public
from server.infrastructure.errors import *
from server.controllers	import *


oauth_linkedin = sc_server.oauth.remote_app(  'linkedin',
		consumer_key=sc_server.config['LINKEDIN_KEY'],
		consumer_secret=sc_server.config['LINKEDIN_SEC'],
		request_token_params={ 'scope': 'r_basicprofile r_emailaddress', 'state': 'deadbeefcafe', },
		base_url='https://api.linkedin.com/v1/',
		request_token_url=None,
		access_token_method='POST',
		access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
		authorize_url   ='https://www.linkedin.com/uas/oauth2/authorization',
)



@public.route('/signin/linkedin', methods=['GET'])
@public.route('/signup/linkedin', methods=['GET'])
def oauth_linkedin_signup_and_signin():
	session['next'] = request.args.get('next') or request.referrer or None
	print 'session.next=',session['next']
	return oauth_linkedin.authorize(callback=url_for('public_routes.linkedin_authorized', _external=True))



@public.route('/authorized/linkedin')
@oauth_linkedin.authorized_handler
def linkedin_authorized(resp):
	if resp is None:
		# Needs a better error page 
		print 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect(request.referrer)

	if isinstance(resp, OAuthException):
		print 'Access denied: %s' % resp.message
		return redirect(request.referrer)


	session['linkedin_token'] = (resp['access_token'], '')

	userinfo = oauth_linkedin.get('people/~:(id,formatted-name,headline,picture-url,industry,summary,skills,recommendations-received,location:(name))')
	userinfo.data['email'] = oauth_linkedin.get('people/~/email-address').data
	#pp (userinfo.data)

	account = sc_authenticate_user_with_oa(OauthProvider.LINKED, userinfo.data)
	if not account: return redirect(request.referrer)

	profile = Profile.get_by_uid(account.userid)
	#import profile
	bind_session(account, profile)

	return redirect('/profile')	#use redirect_back thing



def change_linkedin_query(uri, headers, body):
	auth = headers.pop('Authorization')
	headers['x-li-format'] = 'json'
	if auth:
		auth = auth.replace('Bearer', '').strip()
		if '?' in uri:
			uri += '&oauth2_access_token=' + auth
		else:
			uri += '?oauth2_access_token=' + auth
	return uri, headers, body

oauth_linkedin.pre_request = change_linkedin_query



@oauth_linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')

