import os, json, random, hashlib
import stripe, boto, urlparse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from controllers import *
from datetime import datetime as dt
from datetime import timedelta
from flask import render_template, make_response, session, request, flash, redirect, send_from_directory
from forms import LoginForm, NewAccountForm, ProfileForm, SettingsForm, NewPasswordForm
from forms import NTSForm, SearchForm, ReviewForm, RecoverPasswordForm, ProposalActionForm
from httplib2 import Http
from server import ht_server
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import * 
from server.infrastructure.tasks  import * 
from server.ht_utils import *
from pprint import pprint
from sqlalchemy     import or_
from sqlalchemy.orm import Session
from StringIO import StringIO
from urllib import urlencode
from werkzeug          import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash #rm -- should be in controllers only


# replaced sq.query => db_session.query
# replace db.session => db_session

stripe_keys = {}
stripe_keys['public'] = 'pk_test_ga4TT1XbUNDQ3cYo5moSP66n'
stripe_keys['secret'] = 'sk_test_nUrDwRPeXMJH6nEUA9NYdEJX'
#stripe.api_key = stripe_keys['secret']
            




@ht_server.route('/', methods=['GET', 'POST'])
@ht_server.route('/index')
@dbg_enterexit
def homepage():
	""" Returns the HeroTime front page for users and Heros
		- detect HT Session info.  Provide modified info.
	"""
	if 'uid' in session:
		return redirect('/dashboard')

	return redirect('https://herotime.co/login')



@ht_server.route('/search',  methods=['GET', 'POST'])
@dbg_enterexit
def search():
	""" Provides ability to everyone to search for Heros.  """
	bp       = ""

	if 'uid' in session:
		uid = session['uid']
		bp  = Profile.query.filter_by(account=uid).all()[0]
	
	keywords = request.args.get('search')
	print "keywords = ", keywords
	form = SearchForm(request.form)

	if request.method == 'POST':
		print "is a post" 
		keywords = request.form.get('search')
		#results = db_session.query(Profile).filter_by(location=form.location).all()
		#results = db_session.query(Profile).filter(Profile.bio.like(keywords)).all()
	#results = db_session.query(Profile).all()
	results = db_session.query(Profile)
	print len(results.all())

	if (keywords is not None):
		print "keywords = ", keywords
		rc_name = results.filter(Profile.name.like("%"+keywords+"%"))#.all()
		rc_hdln = results.filter(Profile.headline.like("%"+keywords+"%"))#.all()
		rc_desc = results.filter(Profile.bio.like("%"+keywords+"%")) #.all()
		rc_inds = results.filter(Profile.industry.like("%"+keywords+"%")) #.all()
		#rc_keys = (rc_names + rc_headline + rc_descript)
		print len(rc_name.all()), len(rc_hdln.all()), len(rc_desc.all()), len(rc_inds.all())
		#print len(rc_keys)
		rc_keys = rc_desc.union(rc_hdln).union(rc_name).union(rc_inds).all()
	else:
		rc_keys = results.all()


	resp = make_response(render_template('search.html', bp=bp, form=form, rc_heroes=len(rc_keys), heroes=rc_keys))
	return resp





@ht_server.route('/login', methods=['GET', 'POST'])
@dbg_enterexit
def login():
	""" Logs user into HT system
		Checks if user exists.  
		If successful, sets session cookies and redirects to dash
	"""
	#if already logged in redirect to dashboard
	if ('uid' in session):
		return redirect('/dashboard')

	bp = False
	errmsg = None

	if 'uid' in session:
		uid = session['uid']
		bp  = Profile.query.filter_by(account=uid).all()[0]

	form = LoginForm(request.form)
	if form.validate_on_submit():
		ba = ht_authenticate_user(form.input_login_email.data.lower(), form.input_login_password.data)
		if (ba is not None):
			bp = ht_get_profile(ba)
			ht_bind_session(bp)
			return redirect('/dashboard')

		#flash up there was a failure to login name/pass combo not found
		trace ("POST /login failed, flash name/pass combo failed")
		errmsg = "Incorrect username or password."
	elif request.method == 'POST':
		trace("POST /login form isn't valid" + str(form.errors))
	return make_response(render_template('login.html', title='- Log In', form=form, bp=bp, errmsg=errmsg))



@ht_server.route('/login/linkedin', methods=['GET'])
@dbg_enterexit
def login_linkedin():
	# redirects to LinkedIn, which gets token and comes back to 'authorized'
	session['oauth_signup'] = False
	return linkedin.authorize(callback=url_for('li_authorized', _external=True))


def initProfile(head, ind, loc):
	uid = session['uid']
	bp  = Profile.query.filter_by(account=uid).all()[0]										# Browsing Profile
	trace ("got profile")
	try:
		bp.headline = head
		bp.industry = ind
		bp.location = loc 
		db_session.add(bp)
		db_session.commit()
	except Exception as e:
		trace(str(e))
		db_session.rollback()


@ht_server.route('/login/linkedin/authorized')
@linkedin.authorized_handler
def li_authorized(resp):
	if resp is None:
		# Needs a better error page 
		return 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])

	#assume signup
	#get Oauth Info.
	signup = bool(session.pop('oauth_signup'))
	trace('signup? = ' + str(signup))
	session['linkedin_token'] = (resp['access_token'], '')
	me    = linkedin.get('people/~:(id,formatted-name,headline,picture-url,industry,summary,skills,recommendations-received,location:(name))')
	email = linkedin.get('people/~/email-address')



	# format collected info... prep for init.
	jsondata  = jsonify(me.data)
	linked_id = me.data.get('id')
	user_name = me.data.get('formattedName')
	recommend = me.data.get('recommendationsReceived')
	headline  = me.data.get('headline')
	summary   = me.data.get('summary')
	industry  = me.data.get('industry')
	location  = me.data.get('location')
	trace (str(location))
	trace (str(linked_id))
	trace (email.data)
	trace (user_name)
	trace (headline)
	trace (summary)
	trace (industry)

	# account may exist (email).  -- creat controller: oauth_login(?)
	# deleted if statement because it threw a dbfailure when signing up with an existing account
	#if (not signup):

	possible_acct = Account.query.filter_by(email=email.data).all()
	# also look for linkedin-account/id number (doesn't exist today).
	if (len(possible_acct) == 1):
		# suggest they create a password if that's not done.
		trace('User exists' +  str(possible_acct[0]))
		session['uid'] = possible_acct[0].userid
		return redirect('/dashboard')
	
	# deleted this part in order to successfully signup a user if he does Linkedin oauth from login
	#else:
	#	trace('No account found')
	#	return redirect('/signup')

 	# try creating new account.  We don't know password.
	(bh, bp) = create_account(user_name, email.data, 'linkedin_oauth')
	if (bp):
		trace("created account, uid = " + str(bp.account))
		ht_bind_session(bp)
		initProfile(headline, industry, location)
		trace("called  init profile")

		#Send a welcome email
		send_welcome_email(email.data)
		resp = redirect('/dashboard')
	else:
		# something failed.  
		trace('create account failed, using' + str(email.data))
		resp = redirect('/dbFailure')
	return resp
	#return jsonify(me.data)



@ht_server.route('/signup', methods=['GET', 'POST'])
def signup():

	#if already logged in redirect to dashboard
	if ('uid' in session):
		return redirect('/dashboard')

	bp = False
	if 'uid' in session:
		uid = session['uid']
		bp  = Profile.query.filter_by(account=uid).all()[0]

	form = NewAccountForm(request.form)
	if form.validate_on_submit():
		trace("Validated form -- make Acct")
		(bh, bp) = create_account(form.input_signup_name.data, form.input_signup_email.data.lower(), form.input_signup_password.data)
		if (bh):
			ht_bind_session(bp)
			resp = redirect('/dashboard')
		else:
			resp = redirect('/dbFailure')
		return resp
	elif request.method == 'POST':
		trace("/signup form isn't valid" + str(form.errors))

	return make_response(render_template('signup.html', title='- Sign Up', bp=bp, form=form))



@ht_server.route('/signup/linkedin', methods=['GET'])
@dbg_enterexit
def signup_linkedin():
	# redirects to LinkedIn, which gets token and comes back to 'authorized'
	session['oauth_signup'] = True
	return linkedin.authorize(callback=url_for('li_authorized', _external=True))


@linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')


	
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


@ht_server.route('/signup/verify/<challengeHash>', methods=['GET'])
@dbg_enterexit
def signup_verify(challengeHash):
	rc = None
	# pass in email too... to verify
	# grab info from request parameters
	# 1) challengeHash
	# 2) an email address
	trace("Challenge hash is: " + challengeHash)
	trace(type(challengeHash))

	#Page url
	url = urlparse.urlparse(request.url)
	#Extract query which has email and uid
	query = urlparse.parse_qs(url.query)

	email  = query['email'][0]
	uid  = query['uid'][0]

	accounts = Account.query.filter_by(sec_question=(challengeHash)).all()

	if (len(accounts) != 1 or accounts[0].email != email or accounts[0].userid != uid):
			trace('Hash and/or email didn\'t match.')
			#flash('Hash and/or email didn\'t match.')
			return redirect('/login')

	try:
		hero_account = accounts[0]
		hero_account.set_sec_question("")
		#Email verified

		hero_account.set_status(Account.USER_ACTIVE)
		db_session.commit()
		send_welcome_email(email)
	except Exception as e:
		trace(str(e))
		db_session.rollback()

	# bind session cookie to this 1) Account  and/or 2) this profile 
	bp = Profile.query.filter_by(account=hero_account.userid).all()[0]
	ht_bind_session(bp)
	return make_response(redirect('/dashboard'))




@ht_server.route('/profile', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def profile():
	""" Provides users ability to modify their information.
		- Pre-fill all fields with prior information.
		- Ensure all necessary fields are still populated when submit is hit.
		- update database
	"""

	uid = session['uid']
	bp  = Profile.query.filter_by(account=uid).all()[0]										# Browsing Profile
	hp  = Profile.query.filter_by(heroid=(request.form.get('hero', bp.heroid))).all()[0]		# Hero Profile
	pi  = OauthStripe.query.filter_by(account=hp.account).all()								# Payment info?
#	print "BP = ", bp.name, bp.heroid, bp.account
#	print "HP = ", hp.name, hp.heroid, hp.account
#	print pi, len(pi)

	if (pi):
		pi = pi[0].stripe
		print pi
	else:
		pi = "" 

	nts = NTSForm(request.form)
	if nts.validate_on_submit():
		log_uevent(uid, "creating proposal for " + str(hp.heroid))

		cost   = int(nts.newslot_price.data.replace(',', ''))
		ts_srt = str(nts.newslot_starttime.data)
		ts_end = str(nts.newslot_endtime.data)
		begin  = dt.strptime(nts.datepicker.data  + " " + ts_srt, '%A, %b %d, %Y %H:%M %p')
		finish = dt.strptime(nts.datepicker1.data + " " + ts_end, '%A, %b %d, %Y %H:%M %p')
		bywhom = int(bp.heroid != hp.heroid) 
		timslt = Timeslot(str(hp.heroid), begin, finish, cost, str(nts.newslot_description.data), str(nts.newslot_location.data), creator=str(bp.heroid), status=bywhom)
		try:
			db_session.add(timslt)
			db_session.commit()
			#flash('HT has submitted your proposal')
			#email(hp, bp)
			#add event to users' event queue
			return redirect('/dashboard')

		except Exception as e:
			print e
			db_session.rollback()
			return serviceFailure("profile", e)

	elif request.method == 'POST':
		log_uevent(uid, "POST form isn't valid" + str(nts.errors))
	else:
		pass

	nts.hero.data = hp.heroid


	tmeslts = db_session.query(Timeslot.id, Timeslot.status, Timeslot.location, Timeslot.description, Timeslot.cost, Timeslot.ts_begin, Timeslot.ts_finish, Timeslot.creator_id) \
				.join(Profile, Timeslot.profile_id == Profile.heroid) \
				.filter(Timeslot.profile_id == hp.heroid, Timeslot.status == TS_PROP_BY_HERO).all()
	reviews = db_session.query(Review.heroid, Review.rating, Review.text, Review.ts, Profile.name, Profile.location, Profile.headline, Profile.imgURL, Profile.reviews, Profile.rating, Profile.baserate)\
				.join(Profile, Review.author == Profile.heroid) \
				.filter(Review.heroid == hp.heroid).all()

	profile_img = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(hp.imgURL)
	return make_response(render_template('profile.html', title='- ' + hp.name, hp=hp, bp=bp, revs=reviews, timeslots=tmeslts, ntsform=nts, profile_img=profile_img, key=stripe_keys['public'] ))





@ht_server.route('/cancel', methods=['POST'])
@dbg_enterexit
@req_authentication
def cancelAppt():
	""" Cancels a logged in user's appointment. """
	
	uid = session['uid']
	bp  = Profile.query.filter_by(account=uid).all()[0]
	ts  = Appointment.query.filter_by(id=request.form.get('appt',None)).all()
	print "ts_len" , len(ts)
	if len(ts) == 1:
		print ts
		ts = ts[0]
	print 'bp = ', bp
	print 'ts = ', ts

	try:
		db_session.delete(ts)
		db_session.commit()

		#send emails notifying users.
		print "success, deleted ts"
	except Exception as e:
		print e
		db_session.rollback()
		return serviceFailure("profile", e)

	return make_response(redirect('/dashboard'))





@ht_server.route('/home',      methods=['GET', 'POST'])
@ht_server.route('/dashboard', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def dashboard():
	""" Provides Hero their home.
		- Show calendar with all upcoming ht_serverointments
		- Show any statistics.
	"""

	uid = session['uid']
	bp = Profile.query.filter_by(account=uid).all()[0]
	print 'profile.account = ', uid

	# Reservations?
	# Earnings (this month, last month, year)
	# Reviews, avg review

	# number of appotintments (this week, next week).
	# number of proposals (all)

	#hero = getDossierBySession()
	#hero = getDossierByID()
	title = "- " + bp.name

	# get proposals 

	# get appointments
	timeslot_by_me = db_session.query(Timeslot.id, \
						  Timeslot.status, \
						  Timeslot.location, \
						  Timeslot.description, \
						  Timeslot.cost, \
						  Timeslot.ts_begin, \
						  Timeslot.ts_finish, \
						  Timeslot.profile_id, \
						  Timeslot.creator_id, \
						  Timeslot.challenge, \
						  Profile.heroid, \
						  Profile.name, \
						  Profile.imgURL, \
						  Profile.rating, \
						  Profile.reviews, \
						  Profile.headline) \
						  .join(Profile, Timeslot.profile_id == Profile.heroid) \
						  .filter(Timeslot.creator_id == bp.heroid).all()

	timeslot_to_me = db_session.query(Timeslot.id, \
						  Timeslot.status, \
						  Timeslot.location, \
						  Timeslot.description, \
						  Timeslot.cost, \
						  Timeslot.ts_begin, \
						  Timeslot.ts_finish, \
						  Timeslot.profile_id, \
						  Timeslot.creator_id, \
						  Timeslot.challenge, \
						  Profile.heroid, \
						  Profile.name, \
						  Profile.imgURL, \
						  Profile.rating, \
						  Profile.reviews, \
						  Profile.headline) \
						  .join(Profile, Timeslot.creator_id == Profile.heroid) \
						  .filter(Timeslot.profile_id == bp.heroid).all()

	print "number of timeslots = ", len(timeslot_to_me)

#	prop_to_me = timeslot_to_me.filter(Timeslot.profile_id == bp.heroid).all()
#	prop_by_me = timeslot_to_me.filter(Timeslot.creator_id == bp.heroid).all()
#	print "prop_to_me = ", len(prop_to_me)
#	print "prop_by_me = ", len(prop_by_me)
#	prop = prop_to_me  + prop_by_me
	better_prop = timeslot_to_me + timeslot_by_me
	print "number of total props", len(better_prop)


	for p in better_prop:
		print p

	appt_by_me = db_session.query(Appointment.id, \
							Appointment.status, \
							Appointment.buyer_prof, \
							Appointment.sellr_prof, \
							Appointment.location, \
							Appointment.description, \
							Appointment.ts_begin, \
							Appointment.ts_finish, \
							Appointment.ts_finish, \
							Appointment.cost, \
							Profile.heroid, \
							Profile.name, \
							Profile.imgURL, \
							Profile.reviews, \
							Profile.rating, \
							Profile.headline) \
							.join(Profile, Profile.heroid == Appointment.buyer_prof)\
							.filter(Appointment.sellr_prof == bp.heroid).all()

	appt_of_me = db_session.query(Appointment.id, \
							Appointment.status, \
							Appointment.buyer_prof, \
							Appointment.sellr_prof, \
							Appointment.location, \
							Appointment.description, \
							Appointment.ts_begin, \
							Appointment.ts_finish, \
							Appointment.ts_finish, \
							Appointment.cost, \
							Profile.heroid, \
							Profile.name, \
							Profile.imgURL, \
							Profile.reviews, \
							Profile.rating, \
							Profile.headline) \
							.join(Profile, Profile.heroid == Appointment.sellr_prof)\
							.filter(Appointment.buyer_prof == bp.heroid).all()



#							.filter(or_(Appointment.buyer_prof == bp.heroid, Appointment.sellr_prof == bp.heroid)).all()
	appt_timeslots = appt_of_me + appt_by_me
	print "number of appt_timeslots = ", appt_timeslots


	profile_img = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(bp.imgURL)
	resp = make_response(render_template('dashboard.html', title=title, bp=bp, profile_img=profile_img, ts_prop=better_prop, ts_appt=appt_timeslots))
	return resp



@ht_server.route('/proposals', methods=['POST'])
@dbg_enterexit
@req_authentication
def deal_with_proposals():
	
	log_uevent(session['uid'], " modifying proposal status")
	resp = make_response(redirect('/dashboard'))

	rollback_on_error = False 
	form = ProposalActionForm(request.form)
	try:
		if not form.validate_on_submit():
			log_uevent(session['uid'], "form isnt' valid" + str(form.errors))
			#raise exeception of invalie form 
			return jsonify(invalid='True'), 501

		trace(form.proposal_id.data)
		trace(form.proposal_stat.data)


		rollback_on_error = True
		trace ('search for proposal '  +  form.proposal_id.data) 
		proposal = Timeslot.query.filter_by(challenge=form.proposal_id.data).all()
		if (len(proposal) != 1):
			#raise error
			trace ('natch, len = ' + str(len(proposal))) 
			return jsonify(error='CAH, couldn\'t find proposal'), 501

		trace ('found proposal') 
		the_proposal = proposal[0]

		appointment = Appointment()
		appointment.apptid     = the_proposal.challenge
		appointment.buyer_prof = the_proposal.creator_id
		appointment.sellr_prof = the_proposal.profile_id
		appointment.status		= APPT_HAVE_AGREEMENT
		appointment.location	= the_proposal.location
		appointment.ts_begin	= the_proposal.ts_begin
		appointment.ts_finish 	= the_proposal.ts_finish
		appointment.cust		= "CAH_fake_data"
		appointment.cost		= the_proposal.cost
		appointment.paid		= False
		appointment.description = the_proposal.description
		appointment.created		= the_proposal.created
		appointment.updated		= dt.now()
		print appointment
		trace (appointment) 

		db_session.add(appointment)
		db_session.delete(the_proposal)
		db_session.commit()


	except Exception as e:
		print e
		trace ('hrm, some major error')
		if rollback_on_error:
			db_session.rollback()
		#CAH, this is a problem, how do we signal a problem occurred?
		#flash there was a problem, retry
		trace (e)
		return jsonify(error=e), 500

	return jsonify(tmp="success"), 200



@ht_server.route('/upload', methods=['POST'])
@dbg_enterexit
@req_authentication
def upload():
	log_uevent(session['uid'], " uploading file")
	#trace(request.files)

	for mydict in request.files:
		# for sec. reasons, ensure this is 'edit_profile' or know where it comes from
		trace("reqfiles[" + str(mydict) + "] = " + str(request.files[mydict]))
		image_data = request.files[mydict].read()
		#trace ("img_data type = " + str(type(image_data)) + " " + str(len(image_data)) )
		if (len(image_data) > 0):
			tmp_filename = secure_filename(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			open(os.path.join(ht_server.config['HT_UPLOAD_DIR'], tmp_filename), 'w').write(image_data)
			
		# upload to S3.
		conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
		b = conn.get_bucket(ht_server.config["S3_BUCKET"])
		sml = b.new_key(ht_server.config["S3_DIRECTORY"] + tmp_filename)
		sml.set_contents_from_file(StringIO(image_data))

	return jsonify(tmp="/uploads/" + str(tmp_filename))




@ht_server.route('/edit', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def editprofile():
	""" Provides Hero space to update their information.  """

	uid = session['uid']
	bp  = Profile.query.filter_by(account=uid).all()[0]

	form = ProfileForm(request.form)
	if form.validate_on_submit():
		try:
			trace("PROFILE IS VALID")
			bp.baserate = form.edit_rate.data
			bp.headline = form.edit_headline.data 
			bp.location = form.edit_location.data 
			bp.industry = Industry.industries[int(form.edit_industry.data)] 
			bp.updated  = dt.now()
			bp.name = form.edit_name.data
			bp.bio  = form.edit_bio.data
			bp.url  = form.edit_url.data


			# check for photo, name should be PHOTO_HASH.VER[#].SIZE[SMLX]
			image_data = request.files[form.edit_photo.name].read()
			if (len(image_data) > 0):
				destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
				trace (destination_filename + ", sz = " + str(len(image_data)))
				
				#print source_extension
				conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
				b = conn.get_bucket(ht_server.config["S3_BUCKET"])
				sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
				sml.set_contents_from_file(StringIO(image_data))
				imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
				bp.imgURL = destination_filename

			# ensure 'http(s)://' exists
			if (bp.url[:8] != "https://"):
				if (bp.url[:7] != "http://"):
					bp.url = "http://" + bp.url;

			db_session.commit()
			log_uevent(uid, "update profile")

			return jsonify(rc="Success")
		except Exception as e:
			print e
			db_session.rollback()
			#CAH, this is a problem, how do we signal a problem occurred?
			#flash there was a problem, retry
			return jsonify(error=e)
	elif request.method == 'POST':
		log_uevent(uid, "editform isnt' valid" + str(form.errors))

	x = 0
	for x in range(len(Industry.industries)):
		if Industry.industries[x] == bp.industry:
			form.edit_industry.data = str(x)
			break

	form = ProfileForm(request.form)
	form.edit_name.data     = bp.name
	form.edit_rate.data     = bp.baserate
	form.edit_headline.data = bp.headline
	form.edit_location.data = bp.location
	form.edit_industry.data = str(x)
	form.edit_url.data      = bp.url #replace.httpX://www.
	form.edit_bio.data      = bp.bio
	photoURL 				= 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(bp.imgURL)
	resp = make_response(render_template('edit.html', form=form, bp=bp, photoURL=photoURL))
	
	return resp


@ht_server.route('/charge', methods=['POST'])
@dbg_enterexit
@req_authentication
def charge():
	print "get variables"
	uid = session['uid']
	print "UID", uid
	card = request.form['stripeToken']
	print "get card", card
	tsid = request.form['ts']
	print "get ts", tsid
	ts  = Timeslot.query.filter_by(id=tsid).all()[0]
	ts_owner = ts.profile_id

	bp  = Profile.query.filter_by(account=uid).all()[0]
	ba  = Account.query.filter_by(userid =uid).all()[0]
	hp  = Profile.query.filter_by(heroid=ts.profile_id).all()[0]
	ha  = Account.query.filter_by(userid=hp.account).all()[0]

	pi  = OauthStripe.query.filter_by(account=ha.userid).all()
#	print "BA = ", ba
#	print "HA = ", ha
#	print pi


	charge_api_key = stripe_keys['secret']
	print "charge_key", charge_api_key 
	if (pi):
		charge_api_key = pi[0].token
	print "charge_key", charge_api_key 

	customer = stripe.Customer.create (email=ba.email, card=request.form['stripeToken'], api_key=charge_api_key)
	#pprint(customer)
	


	# get buyer; becomes seller's customer.  
	# get seller's API/ACCESS_TOKEN -- Its like they charge them.  But we need to take API_FEE.
		# perhaps Not Required? -- We could send email stating they can accept and we can write check.  But signup and get paid directly.
	# if seller has pub_key, use it.

#	print 'charge - create customer', card

	charge = stripe.Charge.create (
		customer=customer.id,
		amount=(ts.cost * 100),
		currency='usd',
		description='Flask Charge',
		application_fee=int((ts.cost * 7.1)-30),
		api_key=charge_api_key
		#-- subtracted stripe's fee?  -(30 +(ts.cost * 2.9)  
	)
	#capture too?

	appointment = Appointment()
	#appointment.apptid     = ts.challenge
	appointment.buyer_prof = bp.heroid
	appointment.sellr_prof = hp.heroid
	appointment.status		= APPT_HAVE_AGREEMENT
	appointment.location	= ts.location
	appointment.ts_begin	= ts.ts_begin
	appointment.ts_finish 	= ts.ts_finish
	appointment.cost		= ts.cost
	appointment.paid		= False
	appointment.cust		= customer.id		#stripe.cust.id

	appointment.description = ts.description
	#appointment.transaction	= charge.id 
	appointment.created		= ts.created
	appointment.updated		= ts.updated

	pprint(charge)
	print charge['customer']
	print charge['balance_transaction']
	print charge['failure_code']
	print charge['failure_message']
	print charge['id']

	try:
		db_session.add(appointment)
		db_session.delete(ts)
		db_session.commit()
	except Exception as e:
		db_session.rollback()
		print e
		return redirect('/dbFailure')

	return render_template('charge.html', amount=ts.cost, charge=charge)



@ht_server.route('/proposal', methods=['POST'])
@req_authentication
def create_proposal():
	uid = session['uid']
	log_uevent(session['uid'], " proposing meeting")
	bp = Profile.query.filter_by(account=uid).all()[0]		# browsing profile
	hp  = Profile.query.filter_by(heroid=(request.form.get('hero', bp.heroid))).all()[0]		# Hero Profile
	#trace(request.files)

	nts = NTSForm(request.form)
	if nts.validate_on_submit():
		log_uevent(uid, "creating proposal for " + str(hp.heroid))

		cost   = int(nts.newslot_price.data.replace(',', ''))
		ts_srt = str(nts.newslot_starttime.data)
		ts_end = str(nts.newslot_endtime.data)
		begin  = dt.strptime(nts.datepicker.data  + " " + ts_srt, '%A, %b %d, %Y %H:%M %p')
		finish = dt.strptime(nts.datepicker1.data + " " + ts_end, '%A, %b %d, %Y %H:%M %p')
		bywhom = int(bp.heroid != hp.heroid) 
		timslt = Timeslot(str(hp.heroid), begin, finish, cost, str(nts.newslot_description.data), str(nts.newslot_location.data), creator=str(bp.heroid), status=bywhom)
	else:
		log_uevent(uid, "POST form isn't valid" + str(nts.errors))
		trace(nts.newslot_price.data)
		trace(nts.newslot_starttime.data)
		trace(nts.newslot_endtime.data)

	return jsonify(cost=nts.newslot_price.data, ts_srt1 = str(nts.newslot_starttime.data), ts_end1 = ts_end, begin1=begin, finish1 = finish, bywhom = int(bp.heroid != hp.heroid))




@ht_server.route('/settings', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def settings():
	""" Provides users the ability to modify their settings.
		- detect HT Session info.  Provide modified info.
	"""
	uid = session['uid']
	bp   = Profile.query.filter_by(account=uid).all()[0]
	ba   = Account.query.filter_by(userid=uid).all()[0]
	card = 'Null'
#	card = OauthStripe.query.filter_by(account=uid).all()
#	if (len(card) == 0):
#		print "No stripe account"
#		card = "Payments not setup"
#	else:
#		card = card[0].stripe
#		print "card", card

	errmsg = None
	form = SettingsForm(request.form)
	if form.validate_on_submit():
		print("settings form validated")

		update_acct = False		# requires current_pw_set, 					Sends email
		update_pass = None		# requires current_pw_set, valid new pw =>	Sends email
		update_mail = None

		update_prof = False		# do nothing if above are set.
		update_prop = None
		update_vnty = None
		update_fail = False

		if (form.set_input_newpass.data != ""):
			trace("attempt update pass " + str(ba.pwhash) + " to " +  str(form.set_input_newpass.data))
			update_acct = True
			update_pass = form.set_input_newpass.data
			send_passwd_change_email(ba.email)
			errmsg = "Password successfully updated."

		if (ba.email != form.set_input_email.data):
			trace("attempt update email "  + str(ba.email) +  " to " + str(form.set_input_email.data))
			update_acct = True
			update_mail = form.set_input_email.data

		if (update_acct):
			(rc, errno) = modifyAccount(uid, form.set_input_curpass.data, new_pass=update_pass, new_mail=update_mail)
			trace("modify acct = " + str(rc) + ", errno = " + str(errno))
			if (rc == False):
				trace("restate errno" + str(errno))
				errmsg = str(errno)
				errmsg = error_sanitize(errmsg)
				form.set_input_curpass.data = ''
				form.set_input_newpass.data = ''
				form.set_input_verpass.data = ''
				return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
#				return redirect('/settings')
			else:
				print "Update should be complete"

		if (update_prof):
			try:
				print "update prof"
				db_session.add(bp)
				db_session.commit()
				trace("commited plus email is : " + update_mail)
			except Exception as e:
				db_session.rollback()
				return redirect('/dbFailure')


		#change email; send email to both.
		if (update_mail):
			send_email_change_email(ba.email, form.set_input_email.data)
			errmsg = "Your email has been updated."

		return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
	elif request.method == 'GET':
		pass
	else:
		print "form isnt' valid"
		print form.errors
		errmsg = "Passwords must match."


	form.oauth_stripe.data     = card
	form.set_input_email.data  = ba.email

	return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))


def error_sanitize(message):
	if (message[0:16] == "(IntegrityError)"):
		message = "Email already in use."
	
	return message


@ht_server.route('/settings/verify', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def settings_verify_stripe():
	uid = session['uid']
	bp   = Profile.query.filter_by(account=uid).all()[0]
	acct = Account.query.filter_by(userid=uid).all()[0]

	print "verify -- in oauth_callback, get auth code/token"
	error = request.args.get('error', "None")
	edesc = request.args.get('error_description', "None")
	scope = request.args.get('scope', "None")
	state = request.args.get('state', "None")  #I think state is a CSRF, passed in/passed back
	authr = request.args.get('code',  "None")
	print "scope", scope
	print "auth", authr
	print "error", error
	print "edesc", edesc

	# possible error codes: 
	#	access_denied, 	User denied authorization.
	#	invalid_scope,	Invalid scope parameter provided.... ex. too late / token timeout
	#	invalid_redirect_uri, 	Provided redirect_uri parameter is either an invalid URL or is not allowed by your application settings.
	#	invalid_request, 	Missing response_type parameter.
	# 	unsupported_response_type, 	Unsupported response_type parameter. Currently the only supported response_type is code.
	

	if (authr == "None" and error != "None"):
		print "verify - auth Failed", edesc
		return "auth failed %s" % edesc, 500


	print "verify -- use request Token to get userINFO"
	stripeHTTP = Http()
	postdata = {}
	postdata['client_secret'] = stripe_keys['secret']
	postdata['grant_type']    = 'authorization_code'
	postdata['code']          = authr
	
	print "verify -- post Token to stripe"
	resp, content = stripeHTTP.request("https://connect.stripe.com/oauth/token", "POST", urlencode(postdata))
	rc = json.loads(content)
	print "verify -- got response\n", rc
#	print "error", rc['error']
#	print "edesc", rc['error_description']
#	print "livemode", rc['livemode']
#	print "token", rc['access_token']
#	print "stripe id", rc['stripe_user_id']

	error = rc.get('error',       			 'None') 
	edesc = rc.get('error_description', 	 'None') 
	token = rc.get('access_token',			 'None') 
	mode  = rc.get('livemode',				 'None')
	pkey  = rc.get('stripe_publishable_key', 'None')
	user  = rc.get('stripe_user_id',		 'None')

	if error != 'None':
		print "getToken Failed", edesc
		return "auth failed %s" % edesc, 500

	stripeAccount = OauthStripe.query.filter_by(account=uid).all()
	if len(stripeAccount) == 1:
		stripeAccount = stripeAccount[0]
		if (stripeAccount.stripe != rc['stripe_user_id']):
			stripeAccount.stripe  = rc['stripe_user_id']			# stripe ID.
			print 'changing stripe ID'

		if (stripeAccount.token  != rc['access_token']):
			stripeAccount.token   = rc['access_token']
			print 'changing user-access token, used to deposite into their account'

		if (stripeAccount.pubkey != pkey):
			stripeAccount.pubkey  = pkey
			print 'changing stripe pubkey'
	else:
		stripeAccount = OauthStripe(uid)
		stripeAccount.stripe = rc['stripe_user_id']			# stripe ID.
		stripeAccount.token  = rc['access_token']			# stripe ID.
		stripeAccount.pubkey = rc['stripe_publishable_key']

	try:
		print "try creating oauth_row"
		db_session.add(stripeAccount)
		db_session.commit()
		return make_response(redirect('/settings'))
	except Exception as e:
		print "had an exception with oauth_row" + str(e)
		db_session.rollback()

	return "good - but must've failed on create", 200




@ht_server.route('/terms', methods=['GET'])
def tos():
	bp = False
	if 'uid' in session:
		uid = session['uid']
		bp  = Profile.query.filter_by(account=uid).all()[0]

	return make_response(render_template('tos.html', title = '- Terms and Conditions', bp=bp))



@ht_server.route("/review", methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def review():
	uid = session['uid']
	bp = Profile.query.filter_by(account=uid).all()[0]		# browsing profile
	rp = Profile.query.filter_by(heroid=bp.heroid).all()[0]	# reviewed profile

	review_form = ReviewForm(request.form)
	if review_form.validate_on_submit():
		try:
			# add review to database
			new_review = Review(reviewed_heroid=rp.heroid, author_profile=bp.heroid, rating=5-int(review_form.input_rating.data), text=review_form.input_review.data)
			db_session.add(new_review)
			log_uevent(uid, "posting " + str(new_review))
			
			# update the reviewed profile's ratings, in the future, delay this
			reviews = Review.query.filter_by(heroid=rp.heroid).all()
			sum_ratings = new_review.rating
			for old_review in reviews:
				sum_ratings += old_review.rating

			rp.updated = dt.now()
			rp.reviews = len(reviews) + 1
			rp.rating  = float(sum_ratings) / (len(reviews) + 1)
			log_uevent(rp.heroid, "now has " + str(sum_ratings) + "points, and " + str(len(reviews) + 1) + " for a rating of " + str(rp.rating))
			db_session.add(rp)
			db_session.commit()

			# flash review will be posted at end of daysleft
			# email alt user to know review was captured
			return make_response(redirect('/dashboard'))
		except Exception as e:
			print "had an exception with Review" + str(e)
			db_session.rollback()
	elif request.method == 'POST':
		log_uevent(str(uid), "POST /review isn't valid " + str(review_form.errors))
		pass
	else:
		pass
		
	return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=rp, daysleft=30, form=review_form))


@ht_server.route("/email/<heroName>", methods=['GET'])
def emailHero(heroName):
	#ht_server.logger.debug(request.headers);
	#if (url[:8] != "https://"):
	#	if (url[:7] != "http://"):
	#		url = "HTTP://" + url;
	#uid = htLog('create', request, '{ "reqName" : "' + new + '", "url" : "' + url + '" }')
	print "heroName = '" + heroName + "'"
	email(heroName, "sent from HT")
	return "Good job", 200


@ht_server.route("/heroes/<heroName>", methods=['GET'])
def hero_profile(heroName):
	"""Redirect the request to the URL associated =heroName=."""
	""" otherwise return 404 NOT FOUND"""

	#split profile into a parsing Headers and a 'go get shit' part.
	# this can call into the 'go get shit'
	hero = Profile.query.filter_by(vanity=heroName).all()
	if len(hero) == 1: 
		hp = hero[0]
		
	return pageNotFound('unknown', 404);


@ht_server.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(ht_server.config['HT_UPLOAD_DIR'], filename)


@ht_server.route('/logout', methods=['GET', 'POST'])
def logout():
	session.pop('uid')
	return redirect('/')


@ht_server.errorhandler(404)
def pageNotFound(error):
	return render_template('404.html'), 404


def pageNotFound(pg, error):
	return render_template('404.html'), 404


@ht_server.errorhandler(500)
def servicefailure(pg):
	return render_template('500.html'), 500

def serviceFailure(pg, error):
	return render_template('500.html'), 500


@ht_server.route("/recovery", methods=['GET', 'POST'])
def recovery():
	#mycssfiles = ["static/css/dashboard_lights.css", "static/css/this_is_pretty_cool.css"]
	form = RecoverPasswordForm(request.form)
	usrmsg = None
	if request.method == 'POST':
		trace(form.rec_input_email.data)
		usrmsg = ht_password_recovery(form.rec_input_email.data)
	return render_template('recovery.html', form=form, errmsg=usrmsg)

linkedin.pre_request = change_linkedin_query



@ht_server.route('/newpassword/<challengeHash>', methods=['GET', 'POST'])
def newpassword(challengeHash):

	form = NewPasswordForm(request.form)

	#Page url
	url = urlparse.urlparse(request.url)
	#Extract query which has email and uid
	query = urlparse.parse_qs(url.query)
	if (query):
		email  = query['email'][0]

	accounts = Account.query.filter_by(sec_question=(str(challengeHash))).all()

	if (len(accounts) != 1 or accounts[0].email != email):
			trace('Hash and/or email didn\'t match.')
			#flash('Hash and/or email didn\'t match.')
			return redirect('/login')

	if form.validate_on_submit():
		hero_account = accounts[0]
		hero_account.set_sec_question("")
		hero_account.pwhash = generate_password_hash(form.rec_input_newpass.data)
		trace("New pass is: " + form.rec_input_newpass.data)
		trace("hash " + hero_account.pwhash)

		try:
			db_session.add(hero_account)
			db_session.commit()
			trace("Commited.")
			# Password change email
			send_passwd_change_email(email)
		except Exception as e:
			trace(str(e))
			db_session.rollback()
		return redirect('/login')

	elif request.method == 'POST':
		trace("POST New password isn't valid " + str(form.errors))

	return render_template('newpassword.html', form=form)
