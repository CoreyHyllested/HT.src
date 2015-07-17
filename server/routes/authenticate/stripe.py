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
from server.infrastructure.errors import *
from server.controllers	import *

from httplib2 import Http
from urllib import urlencode


#@public.route('/authorize/stripe', methods=['GET', 'POST'])
@sc_authenticated
def settings_verify_stripe():
	uid = session['uid']
	bp = Profile.get_by_uid(uid)

	print "authorize/stripe"
	error = request.args.get('error', "None")
	edesc = request.args.get('error_description', "None")
	scope = request.args.get('scope', "None")
	state = request.args.get('state', "None")  #I think state is a CSRF, passed in/passed back
	authr = request.args.get('code',  "None")
	print "scope", scope
	print "auth", authr
	print "error", error
	print "edesc", edesc
	print "state", state

	# possible error codes: 
	#	access_denied, 	User denied authorization.
	#	invalid_scope,	Invalid scope parameter provided.... ex. too late / token timeout
	#	invalid_redirect_uri, 	Provided redirect_uri parameter is either an invalid URL or is not allowed by your application settings.
	#	invalid_request, 	Missing response_type parameter.
	# 	unsupported_response_type, 	Unsupported response_type parameter. Currently the only supported response_type is code.


	if (authr == "None" and error != "None"):
		print "verify - auth Failed", edesc
		return "auth failed %s" % edesc, 500


	postdata = {}
	postdata['client_secret'] = sc_server.config['STRIPE_SECRET']
	postdata['grant_type']    = 'authorization_code'
	postdata['code']          = authr

	print "verify -- post Token to stripe"
	#TODO rewrite using Requests library
	resp, content = Http().request("https://connect.stripe.com/oauth/token", "POST", urlencode(postdata))
	rc = json.loads(content)
	print "verify -- got response\n", rc
#	print "error", rc['error']
#	print "edesc", rc['error_description']

	error = rc.get('error',       			 'None') 
	edesc = rc.get('error_description', 	 'None') 
	token = rc.get('access_token',			 'None')	# Used like Secret Key
	mode  = rc.get('livemode',				 'None')
	pkey  = rc.get('stripe_publishable_key', 'None')	# users?!? PK
	user  = rc.get('stripe_user_id',		 'None')	# Customer ID.
	rfrsh = rc.get('refresh_token')

	if error != 'None':
		print "getToken Failed", edesc
		return "auth failed %s" % edesc, 500

	oauth_stripe = Oauth.get_stripe_by_uid(uid)
	if (oauth_stripe is not None):
		if (oauth_stripe.oa_account != rc['stripe_user_id']):
			oauth_stripe.oa_account  = rc['stripe_user_id']
			print 'updating stripe ID'

		if (oauth_stripe.oa_secret != rc['access_token']):
			oauth_stripe.oa_secret  = rc['access_token']
			print 'updating user-access token, used to deposit into their account'

		if (oauth_stripe.oa_token != pkey):
			oauth_stripe.oa_token  = pkey
			print 'updating stripe pubkey'

		if (oauth_stripe.oa_optdata1 != rfrsh):
			oauth_stripe.oa_optdata1  = rfrsh
			print 'updating stripe refresh key'
	else:
		oauth_stripe = Oauth(uid, OAUTH_STRIPE, rc['stripe_user_id'], secret=rc['access_token'], token=rc['stripe_publishable_key'], data1=rfrsh)

	try:
		database.session.add(oauth_stripe)
		database.session.commit()
		next_url = session.pop('next_url', '/settings')
		return make_response(redirect(next_url))
	except Exception as e:
		print type(e), e
		database.session.rollback()
	return "good - but must've failed on create", 200

