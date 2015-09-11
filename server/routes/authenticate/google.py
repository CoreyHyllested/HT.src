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

#https://accounts.google.com/o/oauth2/auth?access_type=offline&response_type=code&redirect_uri=https%3A%2F%2Flocalhost%3A5000%2Fauthorized%2Fgoogle%3Fnext%3Dhttps%253A%252F%252Flocalhost%253A5000%252Fsignup&client_id=877093415096-ukrtt5a5n77og09c0qh32b6fd4obp4oe.apps.googleusercontent.com&hl=en&from_login=1&as=-88fe5cd3fcd49f7&authuser=0
#https://accounts.google.com/o/oauth2/auth?access_type=offline&response_type=code&redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&client_id=407408718192.apps.googleusercontent.com&hl=en&from_login=1&as=-651b76c8f2348df6&authuser=0

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
	#me.data['token']=session['oauth_token']
	print me
#	pp(me)

#	ba = sc_authenticate_user_with_oa(OauthProvider.FACEBK, me.data)
#	if (ba):
#		print ("created_account, uid = " , str(ba.userid), ', get profile')
#		bp = Profile.get_by_uid(ba.userid)
#		bind_session(ba, bp)
#		#import_profile(bp, OauthProvide.FACEBK, oauth_data=me.data)
#		resp = redirect('/profile')
#	else:
#		session['messages'] = 'Account creation failed.'
#		resp = redirect('/signin')

	return jsonify({"data": me.data})
	return resp



@oauth_google.tokengetter
def get_google_oauth_token():
	return session.get('google_token')


#TODO 
# Pop the referred_by / reference values when account creations succeeds.
@testing.route('/google')
def TESTING_render_google_info():
	me = auth_google.get('/me')
	return 'Logged in id=%s name=%s f=%s l=%s email=%s redirect=%s' % (me.data['id'], me.data['name'], me.data['first_name'], me.data['last_name'], me.data['email'], request.args.get('next'))


