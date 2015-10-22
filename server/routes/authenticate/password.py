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

from werkzeug.security	import generate_password_hash

from server.models import *
from server.routes import public_routes as public
from server.routes import api_routing as api
from server.controllers	import *



@public.route('/signup/', methods=['GET'])
@public.route('/signup',  methods=['GET'])
def render_signup_page():
	# if user is logged in, take them to their profile
	if ('uid' in session): return redirect('/profile')
	return make_response(render_template('authorize/signup.html', form=SignupForm(request.values)))



@public.route('/signin/', methods=['GET'])
@public.route('/signin',  methods=['GET'])
def render_signin_page():
	# if user is logged in, take them to their profile
	if ('uid' in session): return redirect('/profile')
	return make_response(render_template('authorize/signin.html', form=SignupForm(request.form)))



@public.route('/modal/signin/',	methods=['GET'])
@public.route('/modal/signin',	methods=['GET'])
@public.route('/modal/login',	methods=['GET'])
def render_signin_modal():
	html_signin	= render_template('authorize/modal-signin.html', form=SignupForm(request.form))
	return make_response(jsonify(embed=html_signin), 200)



#@public.route('/signup/professional/', methods=['GET', 'POST'])
#@public.route('/signup/professional',  methods=['GET', 'POST'])
def render_pro_signup_page(sc_msg=None):
	if ('uid' in session): return redirect('/profile')

	form = ProSignupForm(request.form)
	if form.validate_on_submit(): # and form.terms.data == True:
		try:
			account = Account.create_account(form.uname.data, form.pro_email.data.lower(), form.passw.data, phone=form.pro_phone.data, role=AccountRole.CRAFTSPERSON)
			return make_response(jsonify(next=session.pop('redirect', '/profile')), 200)
		except AccountError as ae:
			pass
	return make_response(render_template('authorize/signup-professional.html', form=form))



@public.route('/authorize/signup/', methods=['POST'])
@public.route('/authorize/signup',  methods=['POST'])
def authorize_password_signup():
	try:
		sf = SignupForm(request.values)
		if not sf.validate_on_submit(): # and form.terms.data == True:
			raise InvalidInput(errors=sf.errors)

		#geo_location = get_geolocation_from_ip()
		account = Account.create_account(sf.uname.data, sf.email.data.lower(), sf.passw.data, ref_id=sf.refid.data)
		profile = Profile.create_profile(account)
		database.session.add(account)
		database.session.add(profile)
		database.session.commit()

		print 'bind-session and cleanup'
		bind_session(account, profile)
		session.pop('ref_id', None)
		session.pop('ref_prof', None)

		email_welcome_message(account.email, account.name, account.sec_question)
		return make_response(jsonify(next=session.pop('redirect', '/profile')), 200)
	except SanitizedException as e:
		print type(e), e
		database.session.rollback()
		return e.make_response()
	except Exception as e:
		print type(e), e
		database.session.rollback()
		return ApiError('An issue occurred while creating an Account').make_response()



@public.route('/authorize/signin/',	methods=['POST'])
@public.route('/authorize/signin',	methods=['POST'])
@sc_server.csrf.exempt
def authorize_password_signin():
	try:
		sf = SignupForm(request.form)
		if not sf.validate_on_submit():
			raise InvalidInput(errors=sf.errors)

		ba = Account.authorize_with_password(sf.email.data.lower(), sf.passw.data)
		if (not ba): raise PasswordError(sf.email.data)

		# successful login, bind session.
		bp = Profile.get_by_uid(ba.userid)
		bind_session(ba, bp)
		return make_response(jsonify(next=session.pop('redirect', '/profile')), 200)

	except SanitizedException as e:
		database.session.rollback()
		return e.make_response()



@public.route('/logout/', methods=['GET', 'POST'])
@public.route('/logout',  methods=['GET', 'POST'])
def logout():
	session.clear()
	return redirect('/')



@public.route('/password/recover/', methods=['GET', 'POST'])
@public.route('/password/recover',  methods=['GET', 'POST'])
def render_password_reset_request(sc_msg=None):
	bp = Profile.get_by_uid(session.get('uid'))

	form = RecoverPasswordForm(request.form)
	if form.validate_on_submit():
		print 'password_reset_request() -', form.email.data
		try:
			sc_password_recovery(form.email.data)
			#session['messages'] = "Reset instructions were sent."
			return make_response(redirect('/signin'))
		except NoEmailFound as nef:
			sc_msg = nef.sanitized_msg()
		except AccountError as ae:
			sc_msg = ae.sanitized_msg()
			print ae
	return render_template('authorize/password-recover.html', bp=bp, form=form, sc_alert=sc_msg)



@api.route('/password/reset', methods=['POST'])
def api_password_reset_request():
	print 'enter api password reset'
	form = RecoverPasswordForm(request.form)

	try:
		if not form.validate_on_submit():
			raise InvalidInput(errors=form.errors)

		print 'password_reset_request() -', form.email.data
		sc_password_recovery(form.email.data)
		return make_response(jsonify(resp='Email sent'), 200)
	except SanitizedException as se:
		#except AccountError
		#except NoEmailFound
		return se.response()
	except Exception as e:
		print type(e), e
		se = SanitizedException(e, status='Oops. An error occurred', code=500)
		return se.response()
		



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
	url302 = session.pop('redirect', next_url)
	return redirect(url302)

