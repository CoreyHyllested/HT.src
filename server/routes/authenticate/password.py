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



@public.route('/signup/', methods=['GET', 'POST'])
@public.route('/signup',  methods=['GET', 'POST'])
def render_signup_page(sc_msg=None):
	if ('uid' in session):
		# if logged in, take 'em home
		return redirect('/profile')

	form = SignupForm(request.values)
	if form.validate_on_submit(): # and form.terms.data == True:
		try:
			profile  = sc_create_account(form.uname.data, form.email.data.lower(), form.passw.data, ref_id=form.refid.data)
			return redirect_back('/profile')
		except AccountError as ae:
			print 'render_signup: error', ae
			sc_msg = ae.sanitized_msg()
	elif request.method == 'POST':
		print 'render_signup: form invalid ' + str(form.errors)
	return make_response(render_template('authorize/signup.html', form=form, sc_alert=sc_msg))




@public.route('/signup/professional/', methods=['GET', 'POST'])
@public.route('/signup/professional',  methods=['GET', 'POST'])
def render_pro_signup_page(sc_msg=None):
	if ('uid' in session):
		# if logged in, take 'em home
		return redirect('/profile')

	form = ProSignupForm(request.form)
	if form.validate_on_submit(): # and form.terms.data == True:
		try:
			profile = sc_create_account(form.uname.data, form.pro_email.data.lower(), form.passw.data, phone=form.pro_phone.data, role=AccountRole.CRAFTSPERSON)
			return redirect_back('/profile')
		except AccountError as ae:
			print 'render_pro_signup: error', ae
			sc_msg = ae.sanitized_msg()
	elif request.method == 'POST':
		print 'render_signup: form invalid ' + str(form.errors)
		sc_msg = 'Oops. Fill out all fields.'
	return make_response(render_template('authorize/signup-professional.html', form=form, sc_alert=sc_msg))




@public.route('/signin/', methods=['GET'])
@public.route('/signin',  methods=['GET'])
def render_signin():
	# user has already logged in; take them home.
	if ('uid' in session): return redirect('/profile')

	return make_response(render_template('authorize/signin.html', form=SignupForm(request.form)))



@public.route('/modal/signin/',	methods=['GET'])
@public.route('/modal/signin',	methods=['GET'])
@public.route('/modal/login',	methods=['GET'])
def render_signin_modal():
	form_signin	= SignupForm(request.form)
	html_signin	= render_template('authorize/modal-signin.html', form=form_signin)
	return make_response(jsonify(embed=html_signin), 200)



@public.route('/authorize/signin/',	methods=['POST'])
@public.route('/authorize/signin',	methods=['POST'])
@sc_server.csrf.exempt
def authorize_password_signin():
	# user has already logged in, take 'em home.
	if ('uid' in session): return redirect('/profile')

	sf = SignupForm(request.form)

	try:
		if not sf.validate_on_submit():
			raise InvalidInput(errors=sf.errors)

		ba = sc_authenticate_user(sf.email.data.lower(), sf.passw.data)
		if (not ba): raise PasswordError(sf.email.data)

		# successful login, bind session.
		bp = Profile.get_by_uid(ba.userid)
		bind_session(ba, bp)
		return make_response(jsonify(next=session.pop('redirect', '/profile')), 200)

	except SanitizedException as e:
		database.session.rollback()
		return e.response()


@public.route('/logout/', methods=['GET', 'POST'])
@public.route('/logout',  methods=['GET', 'POST'])
def logout():
	session.clear()
	return redirect('/')



@public.route("/password/recover/", methods=['GET', 'POST'])
@public.route("/password/recover",  methods=['GET', 'POST'])
def render_password_reset_request(sc_msg=None):
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	form = RecoverPasswordForm(request.form)
	if form.validate_on_submit():
		print 'password_reset_request() -', form.email.data
		try:
			sc_password_recovery(form.email.data)
			session['messages'] = "Reset instructions were sent."
			return make_response(redirect(url_for('public_routes.render_login')))
		except NoEmailFound as nef:
			sc_msg = nef.sanitized_msg()
		except AccountError as ae:
			sc_msg = ae.sanitized_msg()
			print ae
	return render_template('authorize/password-recover.html', bp=bp, form=form, sc_alert=sc_msg)



@public.route('/password/reset/<challengeHash>/', methods=['GET', 'POST'])
@public.route('/password/reset/<challengeHash>',  methods=['GET', 'POST'])
def render_password_reset_page(challengeHash):
	form = NewPasswordForm(request.form)

	url = urlparse.urlparse(request.url)
	#Extract query which has email and uid
	query = urlparse.parse_qs(url.query)
	if (query):
		email  = query['email'][0]

	accounts = Account.query.filter_by(sec_question=(str(challengeHash))).all()
	if (len(accounts) != 1 or accounts[0].email != email):
			trace('Hash and/or email didn\'t match.')
			return redirect('/signin')

	if form.validate_on_submit():
		account = accounts[0]
		account.set_sec_question("")
		account.pwhash = generate_password_hash(form.rec_input_newpass.data)
		trace("hash " + account.pwhash)

		try:
			database.session.add(account)
			database.session.commit()
			sc_send_password_changed_confirmation(email)
		except Exception as e:
			trace(type(e) + ' ' + str(e))
			database.session.rollback()
		return redirect('/signin')
	elif request.method == 'POST':
		trace("POST New password isn't valid " + str(form.errors))
	return render_template('authorize/password-reset.html', form=form)



def redirect_back(next_url):
	return redirect(session.pop('redirect', next_url))
