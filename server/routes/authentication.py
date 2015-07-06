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
from server.routes import sc_ebody, api_routing as api
from server.routes import test_routes as test
from server.infrastructure.errors import *
from server.controllers	import *

from httplib2 import Http
from urllib import urlencode


facebook = sc_server.oauth.remote_app( 'facebook',
		base_url='https://graph.facebook.com',
		request_token_url=None,
		access_token_url='/oauth/access_token',
		authorize_url='https://www.facebook.com/dialog/oauth',
		consumer_key=sc_server.config['FACEBOOK_APP_ID'],
		consumer_secret=sc_server.config['FACEBOOK_APP_SEC'],
		request_token_params={ 'scope': 'email' }
)


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



@sc_ebody.route('/signup/', methods=['GET', 'POST'])
@sc_ebody.route('/signup', methods=['GET', 'POST'])
def render_signup_page(sc_msg=None):
	if ('uid' in session):
		# if logged in, take 'em home
		return redirect('/dashboard')

	form = SignupForm(request.form)
	if form.validate_on_submit(): # and form.terms.data == True:
		try:
			profile  = sc_create_account(form.uname.data, form.email.data.lower(), form.passw.data, ref_id=form.refid.data)
			return redirect('/dashboard')
		except AccountError as ae:
			print 'render_signup: error', ae
			sc_msg = ae.sanitized_msg()
	elif request.method == 'POST':
		print 'render_signup: form invalid ' + str(form.errors)
		sc_msg = 'Oops. Fill out all fields.'

	return make_response(render_template('signup.html', form=form, sc_alert=sc_msg))



@sc_ebody.route('/signup/professional', methods=['GET', 'POST'])
def render_pro_signup_page(sc_msg=None):
	if ('uid' in session):
		# if logged in, take 'em home
		return redirect('/dashboard')

	form = ProSignupForm(request.form)
	if form.validate_on_submit(): # and form.terms.data == True:
		try:
			profile = sc_create_account(form.uname.data, form.pro_email.data.lower(), form.passw.data, phone=form.pro_phone.data, role=AccountRole.CRAFTSPERSON)
			return redirect('/dashboard')
		except AccountError as ae:
			print 'render_pro_signup: error', ae
			sc_msg = ae.sanitized_msg()
	elif request.method == 'POST':
		print 'render_signup: form invalid ' + str(form.errors)
		sc_msg = 'Oops. Fill out all fields.'
	return make_response(render_template('signup-professional.html', form=form, sc_alert=sc_msg))




@sc_server.csrf.exempt
@sc_ebody.route('/login', methods=['GET', 'POST'])
def render_login():
	""" If successful, sets session cookies and redirects to dash """
	sc_msg = session.pop('messages', None)

	if ('uid' in session):
		# user has already logged in.
		return redirect('/dashboard')

	form = LoginForm(request.form)
	if form.validate_on_submit():
		ba = sc_authenticate_user(form.email.data.lower(), form.passw.data)
		if (ba is not None):
			# successful login, bind session.
			bp = Profile.get_by_uid(ba.userid)
			bind_session(ba, bp)
			return redirect('/dashboard')

		trace ("POST /login failed, flash name/pass combo failed")
		sc_msg = "Incorrect username or password."
	elif request.method == 'POST':
		trace("POST /login form isn't valid" + str(form.errors))
		sc_msg = "Incorrect username or password."

	return make_response(render_template('login.html', form=form, sc_alert=sc_msg))




# sends to facebook, which gets token, and user is redirected to 'facebook_authorized'
@sc_ebody.route('/signup/facebook', methods=['GET'])
def oauth_signup_facebook():
	session['oauth_facebook_signup'] = True
	return facebook.authorize(callback=url_for('sc_ebody.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@sc_ebody.route('/login/facebook', methods=['GET'])
def oauth_login_facebook():
	session['oauth_facebook_signup'] = False
	return facebook.authorize(callback=url_for('sc_ebody.facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))



@sc_ebody.route('/authorized/facebook')
@facebook.authorized_handler
def facebook_authorized(resp):
	if resp is None:
		session['messages'] = 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
		return redirect(url_for('sc_ebody.render_login'))

	# User has successfully authenticated with Facebook.
	session['oauth_token'] = (resp['access_token'], '')

	print 'facebook user is creating an account.'
	# grab signup/login info
	me = facebook.get('/me')
	me.data['token']=session['oauth_token']

	ba = sc_authenticate_user_with_oa(OAUTH_FACEBK, me.data)
	if (ba):
		print ("created_account, uid = " , str(ba.userid), ', get profile')
		bp = Profile.get_by_uid(ba.userid)
		print 'bind session'
		bind_session(ba, bp)
		#import_profile(bp, OAUTH_FACEBK, oauth_data=me.data)
		resp = redirect('/dashboard')
	else:
		print ('create account failed')
		resp = redirect('/dbFailure')
	return resp



# redirects to LinkedIn, which gets token and comes back to 'authorized'
@sc_ebody.route('/signup/linkedin', methods=['GET'])
def oauth_signup_linkedin():
	print 'signup_linkedin'
	session['oauth_linkedin_signup'] = True
	return linkedin.authorize(callback=url_for('sc_ebody.linkedin_authorized', _external=True))


@sc_ebody.route('/login/linkedin', methods=['GET'])
def oauth_login_linkedin():
	print 'login_linkedin()'
	session['oauth_linkedin_signup'] = False
	return linkedin.authorize(callback=url_for('sc_ebody.linkedin_authorized', _external=True))



@sc_ebody.route('/authorized/linkedin')
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





@sc_ebody.route('/authorize/stripe', methods=['GET', 'POST'])
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



@facebook.tokengetter
def get_facebook_oauth_token():
	return session.get('oauth_token')


@linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')


@sc_ebody.route('/logout', methods=['GET', 'POST'])
def logout():
	session.clear()
	return redirect('/')



@sc_server.csrf.exempt
@api.route('/login/modal', methods=['POST'])
def api_login_modal():
	# check for session; uid; if so... save
	fragment	= None
	resp_code	= 200
	resp_mesg	= 'Done'

	try:
		# check for data in session; save
		fragment = render_template('fragment_account-create.html')
	except Exception as e:
		#database.session.rollback()
		resp_code = 400
		resp_mesg = 'An error occurred'
	return make_response(jsonify(sc_msg=resp_mesg, embed=fragment), resp_code)




#TODO 
# Pop the referred_by / reference values when account creations succeeds.
@test.route('/facebook')
def TESTING_render_facebook_info():
	me = facebook.get('/me')
	return 'Logged in as id=%s name=%s f=%s l=%s email=%s tz=%s redirect=%s' % (me.data['id'], me.data['name'], me.data['first_name'], me.data['last_name'], me.data['email'], me.data['timezone'], request.args.get('next'))


