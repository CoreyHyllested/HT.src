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


facebook = sc_server.oauth.remote_app( 'facebook',
		base_url='https://graph.facebook.com',
		request_token_url=None,
		access_token_url='/oauth/access_token',
		authorize_url='https://www.facebook.com/dialog/oauth',
		consumer_key=sc_server.config['FACEBOOK_APP_ID'],
		consumer_secret=sc_server.config['FACEBOOK_APP_SEC'],
		request_token_params={ 'scope': 'email' }
)



# sends to facebook, which gets token, and user is redirected to 'facebook_authorized'
@public.route('/signup/facebook', methods=['GET', 'POST'])
def oauth_signup_facebook():
	session['oauth_facebook_signup'] = True
	return facebook.authorize(callback=url_for('public_routes.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))



@public.route('/login/facebook', methods=['GET', 'POST'])
def oauth_login_facebook():
	session['oauth_facebook_signup'] = False
	return facebook.authorize(callback=url_for('public_routes.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))



@public.route('/authorized/facebook')
@facebook.authorized_handler
def facebook_authorized(resp):
	if resp is None:
		session['messages'] = 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect(url_for('public.render_login'))

	# User has successfully authenticated with Facebook.
	session['oauth_token'] = (resp['access_token'], '')

	print 'facebook user is creating an account.'
	# grab signup/login info
	me = facebook.get('/me')
	me.data['token']=session['oauth_token']

	ba = sc_authenticate_user_with_oa(OauthProvider.FACEBK, me.data)
	if (ba):
		print ("created_account, uid = " , str(ba.userid), ', get profile')
		bp = Profile.get_by_uid(ba.userid)
		bind_session(ba, bp)
		#import_profile(bp, OauthProvide.FACEBK, oauth_data=me.data)
		resp = redirect('/profile')
	else:
		session['messages'] = 'Account creation failed.'
		resp = redirect('/login')
	return resp



@facebook.tokengetter
def get_facebook_oauth_token():
	return session.get('oauth_token')


#TODO 
# Pop the referred_by / reference values when account creations succeeds.
@testing.route('/facebook')
def TESTING_render_facebook_info():
	me = facebook.get('/me')
	return 'Logged in id=%s name=%s f=%s l=%s email=%s redirect=%s' % (me.data['id'], me.data['name'], me.data['first_name'], me.data['last_name'], me.data['email'], request.args.get('next'))


