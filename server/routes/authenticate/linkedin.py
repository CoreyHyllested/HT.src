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


linkedin = sc_server.oauth.remote_app(  'linkedin',
		consumer_key=sc_server.config['LINKEDIN_KEY'],
		consumer_secret=sc_server.config['LINKEDIN_SEC'],
		request_token_params={ 'scope': 'r_basicprofile r_emailaddress', 'state': 'deadbeefcafe', },
		base_url='https://api.linkedin.com/v1/',
		request_token_url=None,
		access_token_method='POST',
		access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
		authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)



@public.route('/signup/linkedin', methods=['GET'])
def oauth_signup_linkedin():
	print 'signup_linkedin'
	session['oauth_linkedin_signup'] = True
	# redirects user to LinkedIn; gets login token and user comes home to linkedin_authorized
	return linkedin.authorize(callback=url_for('public.linkedin_authorized', _external=True))


@public.route('/login/linkedin', methods=['GET'])
def oauth_login_linkedin():
	print 'login_linkedin()'
	session['oauth_linkedin_signup'] = False
	# redirects user to LinkedIn; gets login token and user comes home to linkedin_authorized
	return linkedin.authorize(callback=url_for('public.linkedin_authorized', _external=True))



@public.route('/authorized/linkedin')
@linkedin.authorized_handler
def linkedin_authorized(resp):
	print 'login() linkedin_authorized'

	if resp is None:
		# Needs a better error page 
		print 'resp is none'
		return 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])

	#get Oauth Info.
	signup = bool(session.pop('oauth_linkedin_signup'))
	print('li_auth - signup', str(signup))
	print('li_auth - login ', str(not signup))

	session['linkedin_token'] = (resp['access_token'], '')
	ref_id = session.get('ref_id', None)	# Never tested.  Value might not be set.

	me    = linkedin.get('people/~:(id,formatted-name,headline,picture-url,industry,summary,skills,recommendations-received,location:(name))')
	email = linkedin.get('people/~/email-address')

	# format collected info... prep for init.
	print('li_auth - collect data ')
	user_name = me.data.get('formattedName')

	#(bh, bp) = sc_authenticate_user_with_oa(me.data['name'], me.data['email'], OAUTH_FACEBK, me.data)


	# also look for linkedin-account/id number (doesn't exist today).
	possible_accts = Account.query.filter_by(email=email.data).all()
	if (len(possible_accts) == 1):
		# suggest they create a password if that's not done.
		session['uid'] = possible_accts[0].userid
		#return render_dashboard(usrmsg='You haven\'t set a password yet.  We highly recommend you do')
		#save msg elsewhere -- in flags, create table, either check for it in session or dashboard
		return redirect('/dashboard')

 	# try creating new account.  We don't have known password; set to random string and sent it to user.
	print ("attempting create_account(" , user_name , ")")
	try:
		profile = sc_create_account(user_name, email.data, 'linkedin_oauth', ref_id)
		import_profile(profile, OAUTH_LINKED, oauth_data=me.data)

		#send_welcome_email(email.data)
		resp = redirect('/dashboard')
	except AccountError as ae:
		print 'something failed.', ae
		print ('create account failed, using', str(email.data))
		resp = redirect('/dbFailure')
	return resp



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

linkedin.pre_request = change_linkedin_query



@linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')

