#################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
# All Rights Reserved.
#
# All information contained is the property of Insprite, LLC.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Insprite, LLC.
#################################################################################

from . import insprite_views
from flask import render_template
from server import ht_csrf, ht_oauth
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import *
from server.infrastructure.errors import *
from server.controllers	import *
from server.ht_utils	import *
from server.forms import LoginForm, NewAccountForm

facebook = ht_oauth.remote_app( 'facebook',
		base_url='https://graph.facebook.com',
		request_token_url=None,
		access_token_url='/oauth/access_token',
		authorize_url='https://www.facebook.com/dialog/oauth',
		consumer_key=ht_server.config['FACEBOOK_APP_ID'],
		consumer_secret=ht_server.config['FACEBOOK_APP_SEC'],
		request_token_params={ 'scope': 'email' }
)


linkedin = ht_oauth.remote_app(  'linkedin',
					consumer_key=ht_server.config['LINKEDIN_KEY'],
					consumer_secret=ht_server.config['LINKEDIN_SEC'],
					request_token_params={ 'scope': 'r_basicprofile r_emailaddress', 'state': 'deadbeefcafe', },
					base_url='https://api.linkedin.com/v1/',
					request_token_url=None,
					access_token_method='POST',
					access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
					authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)


@insprite_views.route('/signup', methods=['GET', 'POST'])
def render_signup_page(usrmsg = None):
	bp = False

	if ('uid' in session):
		# if logged in, take 'em home
		return redirect('/dashboard')


	form = NewAccountForm(request.form)
	if form.validate_on_submit():
		#check if account (via email) already exists in db
		accounts = Account.query.filter_by(email=form.input_signup_email.data.lower()).all()
		if (len(accounts) == 1):
			trace("email already exists in DB")
			usrmsg = "An account with that email address exists. Login instead?"
		else:
			(bh, bp) = ht_create_account(form.input_signup_name.data, form.input_signup_email.data.lower(), form.input_signup_password.data)
			if (bh):
				ht_bind_session(bp)
				return redirect('/dashboard')
			else:
				usrmsg = 'Something went wrong.  Please try again'
	elif request.method == 'POST':
		usrmsg = 'Form isn\'t filled out properly, ', str(form.errors)
		trace("/signup form isn't valid" + str(form.errors))

	return make_response(render_template('signup.html', title='- Sign Up', bp=bp, form=form, errmsg=usrmsg))




@ht_csrf.exempt
@insprite_views.route('/login', methods=['GET', 'POST'])
@dbg_enterexit
def render_login(usrmsg=None):
	""" Logs user into HT system
		If successful, sets session cookies and redirects to dash
	"""
	bp = None

	if ('uid' in session):
		# user already logged in; take 'em home
		return redirect('/dashboard')

	form = LoginForm(request.form)
	if form.validate_on_submit():
		ba = ht_authenticate_user(form.input_login_email.data.lower(), form.input_login_password.data)
		if (ba is not None):
			bp = Profile.get_by_uid(ba.userid)
			ht_bind_session(bp)
			return redirect('/dashboard')

		trace ("POST /login failed, flash name/pass combo failed")
		usrmsg = "Incorrect username or password."
	elif request.method == 'POST':
		trace("POST /login form isn't valid" + str(form.errors))
		usrmsg = "Incorrect username or password."

	msg = request.values.get('messages')
	if (msg is not None):
		usrmsg = msg

	return make_response(render_template('login.html', title='- Log In', form=form, bp=bp, errmsg=usrmsg))




# sends to facebook, which gets token, and user is redirected to 'facebook_authorized'
@insprite_views.route('/signup/facebook', methods=['GET'])
def oauth_signup_facebook():
	session['oauth_facebook_signup'] = True
	return facebook.authorize(callback=url_for('insprite.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@insprite_views.route('/login/facebook', methods=['GET'])
def oauth_login_facebook():
	session['oauth_facebook_signup'] = False
	return facebook.authorize(callback=url_for('insprite.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))



@insprite_views.route('/authorized/facebook')
@facebook.authorized_handler
def facebook_authorized(resp):
	if resp is None:
		msg = 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect(url_for('render_login', messages=msg))

	# User has successfully authenticated with Facebook.
	session['oauth_token'] = (resp['access_token'], '')

	print 'facebook user is creating an account.'
	# grab signup/login info
	me = facebook.get('/me')
	me.data['token']=session['oauth_token']

	ba = ht_authenticate_user_with_oa(OAUTH_FACEBK, me.data)
	if (ba):
		print ("created_account, uid = " , str(ba.userid), ', get profile')
		bp = Profile.get_by_uid(ba.userid)
		print 'bind session'
		ht_bind_session(bp)
		#import_profile(bp, OAUTH_FACEBK, oauth_data=me.data)
		resp = redirect('/dashboard')
	else:
		print ('create account failed')
		resp = redirect('/dbFailure')
	return resp



# redirects to LinkedIn, which gets token and comes back to 'authorized'
@insprite_views.route('/signup/linkedin', methods=['GET'])
def oauth_signup_linkedin():
	print 'signup_linkedin'
	session['oauth_linkedin_signup'] = True
	return linkedin.authorize(callback=url_for('linkedin_authorized', _external=True))


@insprite_views.route('/login/linkedin', methods=['GET'])
def oauth_login_linkedin():
	print 'login_linkedin()'
	session['oauth_linkedin_signup'] = False
	return linkedin.authorize(callback=url_for('linkedin_authorized', _external=True))



@insprite_views.route('/authorized/linkedin')
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

	me    = linkedin.get('people/~:(id,formatted-name,headline,picture-url,industry,summary,skills,recommendations-received,location:(name))')
	email = linkedin.get('people/~/email-address')

	# format collected info... prep for init.
	print('li_auth - collect data ')
	user_name = me.data.get('formattedName')

	#(bh, bp) = ht_authenticate_user_with_oa(me.data['name'], me.data['email'], OAUTH_FACEBK, me.data)


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
	(bh, bp) = ht_create_account(user_name, email.data, 'linkedin_oauth')
	if (bp):
		print ("created_account, uid = " , str(bp.account))
		ht_bind_session(bp)
		print ("ht_bind_session = ", bp)
		import_profile(bp, OAUTH_LINKED, oauth_data=me.data)

		#send_welcome_email(email.data)
		resp = redirect('/dashboard')
	else:
		# something failed.
		print bh if (bh is not None) else 'None'
		print bp if (bp is not None) else 'None'
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





@insprite_views.route('/authorize/stripe', methods=['GET', 'POST'])
@req_authentication
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
	postdata['client_secret'] = ht_server.config['STRIPE_SECRET']
	postdata['grant_type']    = 'authorization_code'
	postdata['code']          = authr

	print "verify -- post Token to stripe"
	resp, content = Http().request("https://connect.stripe.com/oauth/token", "POST", urlencode(postdata))
	rc = json.loads(content)
	print "verify -- got response\n", rc
#	print "error", rc['error']
#	print "edesc", rc['error_description']

	error = rc.get('error',       			 'None') 
	edesc = rc.get('error_description', 	 'None') 
	token = rc.get('access_token',			 'None')	# Used like Secret Key
	mode  = rc.get('livemode',				 'None')
	pkey  = rc.get('stripe_publishable_key', 'None')
	user  = rc.get('stripe_user_id',		 'None')
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
		db_session.add(oauth_stripe)
		db_session.commit()
		return make_response(redirect('/settings'))
	except Exception as e:
		print type(e), e
		db_session.rollback()
	return "good - but must've failed on create", 200






@facebook.tokengetter
def get_facebook_oauth_token():
	return session.get('oauth_token')


@linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')


@insprite_views.route('/facebook')
def TESTING_render_facebook_info():
	me = facebook.get('/me')
	return 'Logged in as id=%s name=%s f=%s l=%s email=%s tz=%s redirect=%s' % (me.data['id'], me.data['name'], me.data['first_name'], me.data['last_name'], me.data['email'], me.data['timezone'], request.args.get('next'))	
	

@insprite_views.route('/logout', methods=['GET', 'POST'])
def logout():
	session.clear()
	return redirect('/')

