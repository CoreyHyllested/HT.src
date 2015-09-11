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

from server.models import *
from server.routes import public_routes as public
from server.routes import test_routes as testing
from server.infrastructure.errors import *
from server.controllers	import *
from flask_oauthlib.client	import OAuth, OAuthException
from pprint import pprint as pp


oauth_google = sc_server.oauth.remote_app( 'google',
		consumer_key='877093415096-ukrtt5a5n77og09c0qh32b6fd4obp4oe.apps.googleusercontent.com',	# sc_server.config['FACEBOOK_APP_ID'],
		consumer_secret='5Zz7Ewy7ZFR9qZS1pQkE2Dbs',													# sc_server.config['FACEBOOK_APP_SEC'],
		request_token_params={ 'scope': 'https://www.googleapis.com/auth/userinfo.email' },

		base_url='https://www.googleapis.com/oauth2/v1/',
		request_token_url=None,
		access_token_method='POST',
		access_token_url = 'https://accounts.google.com/o/oauth2/token',
		authorize_url    = 'https://accounts.google.com/o/oauth2/auth',
)



# sends to google, which gets token, and user is redirected to 'google_authorized'
@public.route('/signin/google', methods=['GET', 'POST'])
@public.route('/signup/google', methods=['GET', 'POST'])
def oauth_google_signup_and_signin():
	print 'in signup/signin'
	session['next'] = request.args.get('next') or request.referrer or None
	return oauth_google.authorize(callback=url_for('public_routes.google_authorized', _external=True))



@public.route('/authorized/google')
@oauth_google.authorized_handler
def google_authorized(resp):
#	resp = oauth_google.authorized_response()
	if not resp:
		print 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect('/signup')

	if isinstance(resp, OAuthException):
		print 'Access denied: %s' % resp.message
		return redirect('/signup')

	# User has successfully authenticated with Google.
	session['google_token'] = (resp['access_token'], '')

	print 'google user is creating an account.'
	print 'session access_token', resp.get('access_token', 'CAH')
	# grab signup/login info
	me = oauth_google.get('userinfo')
	pp (me.data)

	account = sc_authenticate_user_with_oa(OauthProvider.GOOGLE, me.data)
	if not account: return redirect(request.referrer)

	print "created_account, uid =", str(account.userid), 'get profile'
	profile = Profile.get_by_uid(ba.userid)
	bind_session(account, profile)

	#import_profile(profile, OauthProvide.GOOGLE, oauth_data=me.data)
	return redirect('/profile')



@oauth_google.tokengetter
def get_google_oauth_token():
	return session.get('google_token')

