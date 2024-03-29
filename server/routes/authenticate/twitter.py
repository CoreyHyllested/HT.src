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


oauth_twitter = sc_server.oauth.remote_app( 'twitter',
		consumer_key='6xUFHxYYYNJmHxll0lQbTyMWS', # sc_server.config['FACEBOOK_APP_ID'],
		consumer_secret='Js41wgIRzwDWoz4CFKqwNqjIilX88kRDEYGA6UubtC9XDMXSqz', # sc_server.config['FACEBOOK_APP_SEC'],
		base_url='https://api.twitter.com/1.1/',
		request_token_url = 'https://api.twitter.com/oauth/request_token',
		access_token_url  = 'https://api.twitter.com/oauth/access_token',
		authorize_url     = 'https://api.twitter.com/oauth/authenticate',
)



# sends to twitter, which gets token, and user is redirected to 'twitter_authorized'
@public.route('/signin/twitter/', methods=['GET', 'POST'])
@public.route('/signin/twitter',  methods=['GET', 'POST'])
@public.route('/signup/twitter/', methods=['GET', 'POST'])
@public.route('/signup/twitter',  methods=['GET', 'POST'])
def oauth_twitter_signup_and_signin():
	session['next'] = request.args.get('next') or request.referrer or None
	print 'session.next=',session['next']
	callback_url = url_for('public_routes.twitter_authorized', next=request.args.get('next'))
	return oauth_twitter.authorize(callback=callback_url or request.referrer or None)




@public.route('/authorized/twitter/')
@public.route('/authorized/twitter' )
@oauth_twitter.authorized_handler
def twitter_authorized(resp):
	if not resp:
		print 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect(request.referrer)

	if isinstance(resp, OAuthException):
		print 'Access denied: %s' % resp.message
		return redirect('/signup')

	# User has successfully authenticated with Twitter.
	session['twitter_oauth'] = resp 
	account = sc_authenticate_user_with_oa(OauthProvider.TWITTR, session['twitter_oauth'])
	if not account: return redirect(request.referrer)

	profile = Profile.get_by_uid(account.userid)
	bind_session(account, profile)

	#import_profile(profile, OauthProvide.TWITTR, oauth_data=userinfo.data)
	return redirect('/profile')	#use redirect_back thing



@oauth_twitter.tokengetter
def get_twitter_oauth_token():
	if 'twitter_oauth' in session:
		resp = session.get('twitter_oauth')
		return resp['oauth_token'], resp['oauth_token_secret']


@sc_server.before_request
def before_request():
	g.user = None
	if 'twitter_oauth' in session:
		g.user = session['twitter_oauth']

