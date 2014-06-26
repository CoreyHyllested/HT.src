import os, json, random, hashlib
import stripe, boto, urlparse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from controllers import *
from datetime import datetime as dt, timedelta
from flask import render_template, make_response, session, request, flash, redirect, send_from_directory
from forms import LoginForm, NewAccountForm, ProfileForm, SettingsForm, NewPasswordForm
from forms import NTSForm, SearchForm, ReviewForm, RecoverPasswordForm, ProposalActionForm
from httplib2 import Http
from server import ht_server, ht_csrf, facebook
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import * 
from server.infrastructure.errors import * 
from server.infrastructure.tasks  import * 
from server.ht_utils import *
from pprint import pprint
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError
from StringIO import StringIO
from urllib import urlencode
from werkzeug          import secure_filename
from werkzeug.security import generate_password_hash #rm -- should be in controllers only



@ht_server.route('/', methods=['GET', 'POST'])
@ht_server.route('/index')
@dbg_enterexit
def homepage():
	""" Returns the HeroTime front page for users and Heros
		- detect HT Session info.  Provide modified info.
	"""
	bp = None

	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	return make_response(render_template('index.html', bp=bp))



@ht_csrf.exempt
@ht_server.route('/search',  methods=['GET', 'POST'])
@dbg_enterexit
def render_search():
	""" Provides ability to everyone to search for Heros.  """
	bp = None

	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# get all the search 'keywords'
	keywords = request.values.get('search')
	form = SearchForm(request.form)
	print "keywords = ", keywords

	try:
		results = db_session.query(Profile)
		print 'there are', len(results.all()), 'profiles'

		if (keywords is not None):
			print "keywords = ", keywords
			rc_name = results.filter(Profile.prof_name.ilike("%"+keywords+"%"))
			rc_desc = results.filter(Profile.prof_bio.ilike("%"+keywords+"%"))
			rc_hdln = results.filter(Profile.headline.ilike("%"+keywords+"%"))
			rc_inds = results.filter(Profile.industry.ilike("%"+keywords+"%"))
			print len(rc_name.all()), len(rc_hdln.all()), len(rc_desc.all()), len(rc_inds.all())
	
			# filter by location, use IP as a tell
			rc_keys = rc_desc.union(rc_hdln).union(rc_name).union(rc_inds).all()
		else:
			rc_keys = results.all()
	except Exception as e:
		print e
		db_session.rollback()

	return make_response(render_template('search.html', bp=bp, form=form, rc_heroes=len(rc_keys), heroes=rc_keys))



@ht_csrf.exempt
@ht_server.route('/profile', methods=['GET', 'POST'])
def render_profile(usrmsg=None):
	""" Provides users ability to modify their information.
		- Pre-fill all fields with prior information.
		- Ensure all necessary fields are still populated when submit is hit.
	"""

	bp = None 
	if (session.get('uid') is not None):
		bp = Profile.get_by_uid(session.get('uid'))
		print "BP = ", bp.prof_name, bp.prof_id, bp.account

	try:
		hp = request.values.get('hero')
		if (hp is not None):
			print "hero profile requested,", hp
			hp = Profile.get_by_prof_id(hp)
		else:
			if (bp == None): 
				# no hero requested or logged in. go to login
				return redirect('https://herotime.co/login')	
			hp = bp

		# replace 'hp' with the actual Hero's Profile.
		print "HP = ", hp.prof_name, hp.prof_id, hp.account
	except NoProfileFound as nf:
		print nf
		return jsonify(usrmsg='Sorry, bucko, couldn\'t find who you were looking for -1'), 500
	except Exception as e:
		print e
		return jsonify(usrmsg='Sorry, bucko, couldn\'t find who you were looking for'), 500

	try:
		# complicated search queries can fail and lock up DB.
		portfolio = db_session.query(Image).filter(Image.img_profile == hp.prof_id).all()
		hp_c_reviews = htdb_get_composite_reviews(hp)
	except Exception as e:
		print e
		db_session.rollback()


	print 'images in portfolio:', len(portfolio)
	for img in portfolio: print img
	#portfolio = filter(lambda img: (img.img_flags & IMG_STATE_VISIBLE), portfolio)
	#print 'images in portfolio:', len(portfolio)

	hero_reviews = ht_filter_displayable_reviews(hp_c_reviews, 'REVIEWED', hp, True)
	show_reviews = ht_filter_displayable_reviews(hero_reviews, 'VISIBLE', None, False)

	# TODO: rename NTS => proposal form; hardly used form this.
	nts = NTSForm(request.form)
	nts.hero.data = hp.prof_id
	profile_img = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(hp.prof_img)
	return make_response(render_template('profile.html', title='- ' + hp.prof_name, hp=hp, bp=bp, revs=show_reviews, ntsform=nts, profile_img=profile_img, portfolio=portfolio))






@ht_csrf.exempt
@ht_server.route('/login', methods=['GET', 'POST'])
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



@ht_server.route('/login/facebook', methods=['GET'])
def oauth_login_facebook():
	# redirects to facebook, which gets token and comes back to 'fb_authorized'
	print 'login_facebook()'
	session['oauth_facebook_signup'] = False
	return facebook.authorize(callback=url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@ht_server.route('/login/linkedin', methods=['GET'])
def oauth_login_linkedin():
	# redirects to LinkedIn, which gets token and comes back to 'authorized'
	print 'login_linkedin()'
	session['oauth_linkedin_signup'] = False
	return linkedin.authorize(callback=url_for('linkedin_authorized', _external=True))


@ht_server.route('/authorized/facebook')
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


@facebook.tokengetter
def get_facebook_oauth_token():
	return session.get('oauth_token')

@ht_server.route('/facebook')
def render_facebook_stats():
	me = facebook.get('/me')
	return 'Logged in as id=%s name=%s f=%s l=%s email=%s tz=%s redirect=%s' % (me.data['id'], me.data['name'], me.data['first_name'], me.data['last_name'], me.data['email'], me.data['timezone'], request.args.get('next'))	
	



@linkedin.tokengetter
def get_linkedin_oauth_token():
	return session.get('linkedin_token')

@ht_server.route('/authorized/linkedin')
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



@ht_server.route('/signup', methods=['GET', 'POST'])
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



@ht_server.route('/signup/facebook', methods=['GET'])
def signup_facebook():
	session['oauth_facebook_signup'] = True
	return facebook.authorize(callback=url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@ht_server.route('/signup/linkedin', methods=['GET'])
def signup_linkedin():
	print 'signup_linkedin'
	session['oauth_linkedin_signup'] = True
	return linkedin.authorize(callback=url_for('linkedin_authorized', _external=True))



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





@ht_server.route('/schedule', methods=['GET','POST'])
@req_authentication
def render_schedule_page():
	""" Schedule a new appointment appointment. """

	usrmsg = None
	hp_id = request.values.get('hp', None)
	bp = Profile.get_by_uid(session.get('uid'))
	hp = Profile.get_by_prof_id(request.values.get('hp', None))
	ba = Account.get_by_uid(session.get('uid'))
	if (ba.status == Account.USER_UNVERIFIED):
		return make_response(redirect(url_for('render_settings', nexturl='/schedule?hp='+request.args.get('hp'), messages='You must verify email before scheduling.')))

	nts = NTSForm(request.form)
	nts.hero.data = hp.prof_id

	return make_response(render_template('schedule.html', bp=bp, hp=hp, form=nts, errmsg=usrmsg))




@ht_server.route('/proposal/create', methods=['POST'])
@req_authentication
def ht_api_proposal_create():
	user_message = 'Interesting'

	try:
		print 'ht_api_proposal_create'
		proposal = ht_proposal_create(request.values, session['uid'])
		if (proposal is not None): user_message = 'Successfully created proposal'
	except Sanitized_Exception as se:
		user_message = se.get_sanitized_msg()
		return make_response(jsonify(usrmsg=user_message), se.httpRC())
	except Exception as e:
		print type(e), e
		return make_response(jsonify(usrmsg='Something bad'), 500)
	return make_response(jsonify(usrmsg=user_message, nexturl="/dashboard"), 200)



@ht_server.route('/proposal/accept', methods=['POST'])
@req_authentication
def ht_api_proposal_accept():
	form = ProposalActionForm(request.form)
	pstr = "wants to %s proposal (%s); challenge_hash = %s" % (form.proposal_stat.data, form.proposal_id.data, form.proposal_challenge.data)
	log_uevent(session['uid'], pstr)

	if not form.validate_on_submit():
		msg = "invalid form: " + str(form.errors)
		log_uevent(session['uid'], msg) 
		return jsonify(usrmsg=msg), 503

	try:
		rc, msg = ht_proposal_accept(form.proposal_id.data, session['uid'])
		print rc, msg
	except Sanitized_Exception as se:
		return jsonify(usrmsg=se.get_sanitized_msg()), 500
	except Exception as e:
		print str(e)
		db_session.rollback()
		jsonify(usrmsg=str(e)), 500
	return make_response(redirect('/dashboard'))




@ht_server.route('/proposal/reject', methods=['POST'])
@req_authentication
def ht_api_proposal_reject():
	form = ProposalActionForm(request.form)
	pstr = "wants to %s proposal (%s); challenge_hash = %s" % (form.proposal_stat.data, form.proposal_id.data, form.proposal_challenge.data)
	log_uevent(session['uid'], pstr)


	if not form.validate_on_submit():
		msg = "invalid form: " + str(form.errors)
		log_uevent(session['uid'], msg) 
		return jsonify(usrmsg=str(msg)), 504

	try:
		rc, msg = ht_proposal_reject(form.proposal_id.data, session['uid'])
	except NoProposalFound as npf:
		print rc, msg
		return jsonify(usrmsg="Weird, proposal doesn\'t exist"), 505
	except StateTransitionError as ste:
		db_session.rollback()
		print ste, ste.get_sanitized_msg()
		return jsonify(usrmsg=ste.get_sanitized_msg()), 500
	except DB_Error as ste:
		db_session.rollback()
		print ste
		return jsonify(usrmsg="Weird, some DB problem, try again"), 505
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify(usrmsg="Weird, some unknown issue: "+ str(e)), 505
	print rc, msg
	return jsonify(usrmsg="Proposal Deleted"), 200





@ht_server.route('/proposal/negotiate', methods=['POST'])
@req_authentication
def ht_api_proposal_negotiate():
	#the_proposal = Proposal.get_by_id(form.proposal_id.data)
	#the_proposal.set_state(APPT_STATE_RESPONSE)
	#the_proposal.prop_count = the_proposal.prop_count + 1
	#the_proposal.prop_updated = dt.now()
	return redirect('/notImplemented')


	


@ht_server.route('/appointment/cancel', methods=['POST'])
@dbg_enterexit
@req_authentication
def ht_api_appt_cancel():
	""" Cancels a logged in user's appointment. """

	uid = session['uid']
	print 'apptid = ', request.values.get('appt_id', 'Nothing found here, sir')

	try:
		the_proposal = Proposal.get_by_id(request.values.get('appt_id'))
		the_proposal.set_state(APPT_STATE_CANCELED)
		db_session.add(the_proposal)
		db_session.commit()
		print the_proposal

		#send emails notifying users.
		print "success, canceled appt"
	except DB_Error as dbe:
		print dbe
		db_session.rollback()
		return jsonify(usrmsg="Weird, some DB problem, try again"), 505
	except StateTransitionError as ste:
		print ste
		db_session.rollback()
		return jsonify(usrmsg=ste.get_sanitized_msg()), 500
	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg=nre), 400
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify(usrmsg='Bizarre, something failed'), 500

	return jsonify(usrmsg="succesfully canceled proposal"), 200





@ht_server.route('/home',      methods=['GET', 'POST'])
@ht_server.route('/dashboard', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def render_dashboard(usrmsg=None):
	""" Provides Hero their personalized homepage.
		- Show calendar with all upcoming appointments
		- Show any statistics.
	"""

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	print 'profile.account = ', uid, bp

	hero = aliased(Profile, name='hero')
	user = aliased(Profile, name='user')
	unread_msgs = []

	try:
		appts_and_props = db_session.query(Proposal, user, hero)														\
									.filter(or_(Proposal.prop_user == bp.prof_id, Proposal.prop_hero == bp.prof_id))	\
									.join(user, user.prof_id == Proposal.prop_user)										\
									.join(hero, hero.prof_id == Proposal.prop_hero).all();
		unread_msgs = ht_get_unread_messages(bp)
	except Exception as e:
		print type(e), e
		db_session.rollback()
	
	map(lambda msg: display_partner_message(msg, bp.prof_id), unread_msgs)
	map(lambda anp: display_partner_proposal(anp, bp.prof_id), appts_and_props)
	props = filter(lambda p: ((p.Proposal.prop_state == APPT_STATE_PROPOSED) or (p.Proposal.prop_state == APPT_STATE_RESPONSE)), appts_and_props)
	appts = filter(lambda a: ((a.Proposal.prop_state == APPT_STATE_ACCEPTED) or (a.Proposal.prop_state == APPT_STATE_CAPTURED) or (a.Proposal.prop_state == APPT_STATE_OCCURRED)), appts_and_props)

	return make_response(render_template('dashboard.html', title="- " + bp.prof_name, bp=bp, proposals=props, appointments=appts, messages=unread_msgs, errmsg=usrmsg))



def display_partner_proposal(p, user_is):
	if (user_is == p.Proposal.prop_hero): 
		#user it the hero, we should display all the 'user'
		print p.Proposal.prop_uuid, 'matches hero (', p.Proposal.prop_hero, ',', p.hero.prof_name ,') set display to user',  p.user.prof_name
		setattr(p, 'display', p.user) 
		setattr(p, 'sellr', True) 
		setattr(p, 'buyer', False) 
	else:
		print p.Proposal.prop_uuid, 'matches hero (', p.Proposal.prop_user, ',', p.user.prof_name ,') set display to hero',  p.hero.prof_name
		setattr(p, 'display', p.hero)
		setattr(p, 'buyer', True) 
		setattr(p, 'sellr', False) 


def display_partner_message(msg, prof_id):
	display_prof = (prof_id == msg.UserMessage.msg_to) and msg.msg_from or msg.msg_to
	setattr(msg, 'display', display_prof)



@ht_server.route('/upload', methods=['POST'])
@dbg_enterexit
@req_authentication
def upload():
	log_uevent(session['uid'], " uploading file")
	#trace(request.files)
	print 'enter'

	bp = Profile.get_by_uid(session.get('uid'))
	orig = request.values.get('orig')
	prof = request.values.get('prof')


	print 'orig', orig
	print 'prof', prof

	for mydict in request.files:

		comment = ""

		# for sec. reasons, ensure this is 'edit_profile' or know where it comes from
		print("reqfiles[" + str(mydict) + "] = " + str(request.files[mydict]))
		image_data = request.files[mydict].read()
		print ("img_data type = " + str(type(image_data)) + " " + str(len(image_data)) )

		#trace ("img_data type = " + str(type(image_data)) + " " + str(len(image_data)) )
		if (len(image_data) > 0):
			# create Image.
			img_hashname = secure_filename(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			metaImg = Image(img_hashname, bp.prof_id, comment)
			f = open(os.path.join(ht_server.config['HT_UPLOAD_DIR'], img_hashname), 'w')
			f.write(image_data)
			f.close()
			try:
				print 'adding metaimg to db'
				db_session.add(metaImg)
				db_session.commit()
			except Exception as e:
				print e
				db_session.rollback()


		# upload to S3.
		conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
		b = conn.get_bucket(ht_server.config["S3_BUCKET"])
		sml = b.new_key(ht_server.config["S3_DIRECTORY"] + img_hashname)
		sml.set_contents_from_file(StringIO(image_data))

	return jsonify(tmp="/uploads/" + str(img_hashname))




@ht_server.route('/sendmsg', methods=['POST'])
@req_authentication
def ht_api_send_message():
	""" Send a user message. """

	uid = session['uid']

	try:
		bp = Profile.get_by_uid(session['uid'])

		msg_from = bp.prof_id
		msg_to	= request.values.get('hp')
		content	= request.values.get('msg')
		parent	= request.values.get('msg_parent')
		thread	= request.values.get('msg_thread')
		subject = request.values.get('subject')
		next	= request.values.get('next')

		print
		print "/sendmsg - MESSAGE DETAILS"
		print 'message from ' + bp.prof_name
		print 'message to ' + msg_to
		print 'subject=', subject
		print 'parent=', parent
		print 'thread=', thread
		print 'next=', next

		if (parent):
			# print ('get thread leader', thread)
			msg_thread_leader = UserMessage.get_by_msg_id(thread)
			#if (msg_thread_leader.msg_to != bp.prof_id or msg_thread_leader.msg_from != bp.prof_id):
				# prevent active tampering.
				#return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500
			msg_to = (msg_thread_leader.msg_to != bp.prof_id) and msg_thread_leader.msg_to or msg_thread_leader.msg_from

			# set thread updated flag and clear archive flags for both users.
			archive_flags = (MSG_STATE_RECV_ARCHIVE | MSG_STATE_SEND_ARCHIVE)
			msg_thread_leader.msg_flags = msg_thread_leader.msg_flags | MSG_STATE_THRD_UPDATED
			msg_thread_leader.msg_flags = msg_thread_leader.msg_flags & ~(archive_flags)
			db_session.add(msg_thread_leader)

		message = UserMessage(msg_to, bp.prof_id, content, subject=subject, thread=thread, parent=parent)
		
		db_session.add(message)
		db_session.commit()

		hp = Profile.get_by_prof_id(msg_to)
		email_user_to_user_message(bp, hp, subject, thread, message)
		return make_response(jsonify(usrmsg="Message sent.", next=next, valid="true"), 200)

	except DB_Error as dbe:
		print dbe
		db_session.rollback()
		return jsonify(usrmsg="Weird, some DB problem, try again", next=next, valid="true"), 505
	except NoResourceFound as nre:
		print nre
		return jsonify(usrmsg="Weird, couldn't find something", next=next, valid="true"), 505
	except Exception as e:
		print type(e)
		print e
		db_session.rollback()
		return jsonify(usrmsg='Bizarre, something failed', next=next, valid="true"), 500



@ht_server.route('/edit', methods=['GET', 'POST'])
#@dbg_enterexit
@req_authentication
def render_edit():
	""" Provides Hero space to update their information.  """

	print 'enter edit'
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)

	form = ProfileForm(request.form)
	if form.validate_on_submit():
		try:
			print ("form is valid")
			bp.prof_rate = form.edit_rate.data
			bp.headline = form.edit_headline.data 
			bp.location = form.edit_location.data 
			bp.industry = Industry.industries[int(form.edit_industry.data)] 
			bp.prof_name = form.edit_name.data
			bp.prof_bio  = form.edit_bio.data
			bp.prof_url  = form.edit_url.data

			#TODO: re-enable this; fails on commit (can't compare offset-naive and offset-aware datetimes)
			# bp.updated  = dt.utcnow()

			# check for photo, name should be PHOTO_HASH.VER[#].SIZE[SMLX]
			image_data = request.files[form.edit_photo.name].read()
			if (len(image_data) > 0):
				destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
				trace (destination_filename + ", sz = " + str(len(image_data)))

				#print source_extension
				print 's3'
				conn = boto.connect_s3(ht_server.config["S3_KEY"], ht_server.config["S3_SECRET"]) 
				b = conn.get_bucket(ht_server.config["S3_BUCKET"])
				sml = b.new_key(ht_server.config["S3_DIRECTORY"] + destination_filename)
				sml.set_contents_from_file(StringIO(image_data))
				imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
				bp.prof_img = destination_filename

			# ensure 'http(s)://' exists
			if (bp.prof_url[:8] != "https://"):
				if (bp.prof_url[:7] != "http://"):
					bp.prof_url = "http://" + bp.prof_url;

			print 'add'
			db_session.add(bp)
			print 'commit'
			db_session.commit()
			log_uevent(uid, "update profile")

			return jsonify(usrmsg="profile updated"), 200

		except AttributeError as ae:
			print 'hrm. must have changed an object somehwere'
			print ae
			db_session.rollback()
			return jsonify(usrmsg='We messed something up, sorry'), 500

		except Exception as e:
			print e
			db_session.rollback()
			return jsonify(usrmsg=e), 500

	elif request.method == 'POST':
		log_uevent(uid, "editform isnt' valid" + str(form.errors))
		print 'shoulding this fire?'
		return jsonify(usrmsg='Invalid Request: ' + str(form.errors)), 500

	x = 0
	for x in range(len(Industry.industries)):
		if Industry.industries[x] == bp.industry:
			form.edit_industry.data = str(x)
			break

	form = ProfileForm(request.form)
	form.edit_name.data     = bp.prof_name
	form.edit_rate.data     = bp.prof_rate
	form.edit_headline.data = bp.headline
	form.edit_location.data = bp.location
	form.edit_industry.data = str(x)
	form.edit_url.data      = bp.prof_url #replace.httpX://www.
	form.edit_bio.data      = bp.prof_bio
	photoURL 				= 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/' + str(bp.prof_img)
	return make_response(render_template('edit.html', form=form, bp=bp, photoURL=photoURL))



def sanitize_render_errors(err):
	print 'caught error:' + str(err)









@ht_server.route('/settings', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def render_settings():
	""" Provides users the ability to modify their settings.
		- detect HT Session info.  Provide modified info.
	"""
	uid = session['uid']
	bp	= Profile.get_by_uid(uid)
	ba	= Account.get_by_uid(uid)
	#pi	= Oauth.get_stripe_by_uid(uid)

	card = 'Null'


	errmsg = None
	form = SettingsForm(request.form)
	if form.validate_on_submit():
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

		if (ba.email != form.set_input_email.data):
			trace("attempt update email "  + str(ba.email) +  " to " + str(form.set_input_email.data))
			update_acct = True
			update_mail = form.set_input_email.data

		if (update_acct):
			if (update_pass):
				pwd = form.set_input_curpass.data
			else:
				pwd = form.set_input_email_pass.data
			trace("password is: " + pwd)
			(rc, errno) = modifyAccount(uid, pwd, new_pass=update_pass, new_mail=update_mail)
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

		#change pass send email
		if (update_pass):
			send_passwd_change_email(ba.email)
			errmsg = "Password successfully updated."

		return make_response(render_template('settings.html', form=form, bp=bp, errmsg=errmsg))
	elif request.method == 'GET':
		msg = request.values.get('messages')
		if (msg is not None): errmsg = msg
	else:
		print "form isnt' valid"
		print form.errors
		errmsg = "Passwords must match."


	email_unver = False
	if (ba.status == Account.USER_UNVERIFIED):
		print bp.prof_name, ' email is unverified'
		email_unver = True

	form.oauth_stripe.data     = card
	form.set_input_email.data  = ba.email
	nexturl = "/settings"
	if (request.values.get('nexturl') is not None):
		nexturl = request.values.get('nexturl')

	return make_response(render_template('settings.html', form=form, bp=bp, nexturl=nexturl, unverified_email=email_unver, errmsg=errmsg))


def error_sanitize(message):
	if (message[0:16] == "(IntegrityError)"):
		message = "Email already in use."

	return message


@ht_server.route('/settings/verify', methods=['GET', 'POST'])
@dbg_enterexit
@req_authentication
def settings_verify_stripe():
	uid = session['uid']
	bp = Profile.get_by_uid(uid)

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
	postdata['client_secret'] = ht_server.config['STRIPE_SECRET']
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

	stripeAccount = Oauth.query.filter_by(account=uid).all()
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
		stripeAccount = Oauth(uid, OAUTH_STRIPE, rc['stripe_user_id'], token=rc['access_token'], data3=rc['stripe_publishable_key'])

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
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	return make_response(render_template('tos.html', title = '- Terms and Conditions', bp=bp))



@ht_server.route("/review/<appt_id>/<review_id>", methods=['GET', 'POST'])
@req_authentication
def render_review_page(appt_id, review_id):
	uid = session['uid']

	try:
		bp = Profile.get_by_uid(session['uid'])
		print appt_id, ' = id of Appt'
		print review_id, ' = id of Review'
		the_review = Review.retreive_by_id(review_id)[0] 
		print the_review


		the_review.validate(bp.prof_id)
		print 'we\'re the intended audience'

		print the_review.prof_authored
		print uid
		print dt.utcnow()

		bp = Profile.get_by_uid(session['uid'])					# authoring profile
		rp = Profile.get_by_prof_id(the_review.prof_reviewed)	# reviewed  profile


		days_since_created = timedelta(days=30) # + the_review.rev_updated - dt.utcnow()  #CAH FIXME TODO
		#appt = Appointment.query.filter_by(apptid=the_review.appt_id).all()[0]
		#show the -cost, -time, -description, -location
		#	were you the buyer or seller.  the_appointment.hero; the_appointment.sellr_prof

		review_form = ReviewForm(request.form)
		review_form.review_id.data = str(review_id)
		return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=rp, daysleft=str(days_since_created.days), form=review_form))

	except NoReviewFound as rnf:
		print rnf 
		db_session.rollback()
		return jsonify(usrmsg=rnf.msg)
	except ReviewError as re:
		print re
		db_session.rollback()
		return jsonify(usrmsg=re.msg)
	except Exception as e:
		print e
		db_session.rollback()
		return redirect('/failure')
	except IndexError as ie:
		print 'trying to access, review, author or reviewer account and fialed'
		db_session.rollback()
		return redirect('/dbFailure')





@ht_server.route("/postreview", methods=['GET','POST'])
@req_authentication
def review():
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	print 'enter postreview'

	review_form = ReviewForm(request.form)
	print 'got form'

	print review_form
	print review_form.input_rating.data
	print review_form.input_review.data
	print review_form.review_id.data
	print review_form.score_comm.data
	print review_form.score_time.data

	if review_form.validate_on_submit():
		print 'form is valid'
		try:
			# add review to database
			the_review = Review.retreive_by_id(review_form.review_id.data)[0]
			the_review.appt_score = int(review_form.input_rating.data)
			the_review.generalcomments = review_form.input_review.data
			the_review.score_attr_comm = int(review_form.score_comm.data)
			the_review.score_attr_time = int(review_form.score_time.data)
			the_review.rev_status = the_review.rev_status | REV_STATE_VISIBLE
			rp = Profile.get_by_prof_id(the_review.prof_reviewed)	# reviewed  profile
			print 'form is updated'

			db_session.add(the_review)
			log_uevent(uid, "posting " + str(the_review))

			# update the reviewed profile's ratings, in the future, delay this
			# kick this out to another function.  
			reviews = Review.query.filter_by(prof_reviewed = rp.prof_id).all()
			sum_ratings = the_review.appt_score
			for old_review in reviews:
				sum_ratings += old_review.appt_score

			rp.updated = dt.now()
			rp.reviews = len(reviews) + 1
			rp.rating  = float(sum_ratings) / (len(reviews) + 1)
			log_uevent(rp.prof_id, "now has " + str(sum_ratings) + "points, and " + str(len(reviews) + 1) + " for a rating of " + str(rp.rating))
			db_session.add(rp)
			db_session.commit()
			print 'data has been posted'

			# flash review will be posted at end of daysleft
			# email alt user to know review was captured
			return make_response(redirect('/dashboard'))
		except Exception as e:
			print "had an exception with Review" + str(e)
			db_session.rollback()
			log_uevent(str(uid), "POST /review isn't valid " + str(review_form.errors))
			return jsonify(usrmsg='Data invalid')
	elif request.method == 'POST':
		print "POST New password isn't valid " + str(review_form.errors)
		return jsonify(usrmsg=str(review_form.errors))
	else:
		print "form wasn't posted"
		
	return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=bp, daysleft=str(28), form=review_form))




@ht_server.route('/uploads/<filename>')
def uploaded_file(filename):
	# add sec protection?
	return send_from_directory(ht_server.config['HT_UPLOAD_DIR'], filename)


@ht_server.route('/logout', methods=['GET', 'POST'])
def logout():
	session.clear()
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


linkedin.pre_request = change_linkedin_query



@ht_server.route("/email/<operation>/<data>", methods=['GET','POST'])
def ht_email_operations(operation, data):
	print operation, data
	if (operation == 'verify'):
		email = request.values.get('email_addr')
		nexturl = request.values.get('next_url')
		print 'verify: data  = ', data, 'email =', email
		return ht_email_verify(email, data, nexturl)
	elif (operation == 'request-response'):
		nexturl = request.values.get('nexturl')
		return make_response(render_template('verify_email.html', nexturl=nexturl))
	elif (operation == 'request-verification') and ('uid' in session):

		bp = Profile.get_by_uid(session.get('uid'))
		ba = Account.get_by_uid(session.get('uid'))
		email_set = set([ba.email, request.values.get('email_addr')])
		print email_set
		ht_send_verification_to_list(ba, bp, email_set)
		return jsonify(rc=200), 200
	return pageNotFound('Not sure what you were looking for')




def ht_send_verification_to_list(account, profile, email_set):
	print 'ht_send_verification_to_list'
	challenge_hash = str(uuid.uuid4())
	account.set_sec_question(challenge_hash)

	try:
		db_session.add(account)
		db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	for email in email_set:
		print 'sending email to', email
		send_verification_email(email, profile.prof_name, challenge_hash)



def ht_email_verify(email, challengeHash, nexturl=None):
	accounts = Account.query.filter_by(sec_question=(challengeHash)).all()

	if (len(accounts) != 1 or accounts[0].email != email):
			msg = 'Verification code for user, ' + str(email) + ', didn\'t match the one on file.'
			return redirect(url_for('render_login', messages=msg))

	try:
		print 'update user account'
		# update user's account.
		account = accounts[0]
		account.set_email(email)
		account.set_sec_question("")
		account.set_status(Account.USER_ACTIVE)

		db_session.add(account)
		db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	# bind session cookie to this user's profile
	bp = Profile.get_by_uid(account.userid)
	send_welcome_email(email, bp.prof_name)
	ht_bind_session(bp)
	if (nexturl is not None):
		# POSTED from jquery in /settings:verify_email not direct GET
		return make_response(jsonify(usrmsg="Account Updated."), 200)
	return make_response(redirect('/dashboard'))




@ht_server.route("/password/recover", methods=['GET', 'POST'])
def ht_password_recover():
	form = RecoverPasswordForm(request.form)
	usrmsg = None
	if request.method == 'POST':
		trace(form.rec_input_email.data)
		usrmsg = ht_password_recovery(form.rec_input_email.data)
	return render_template('recovery.html', form=form, errmsg=usrmsg)




@ht_server.route('/password/reset/<challengeHash>', methods=['GET', 'POST'])
def ht_password_reset(challengeHash):
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



@ht_server.route("/dmca", methods=['GET', 'POST'])
def render_dmca_page():
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('dmca.html', bp=bp))
	



@ht_server.route("/fakereview/<buyer>/<sellr>", methods=['GET'])
def render_rake_page(buyer, sellr):

	print 'ready to get uid'
	bp = Profile.get_by_prof_id(str(buyer))
	print 'buyer', bp

	sp = Profile.get_by_prof_id(str(sellr))
	print 'sellr', sp

	values = {}
	values['stripe_tokn'] = 'abc123'
	values['stripe_card'] = '4242424242424242'
	values['stripe_cust'] = 'cus_100'
	values['stripe_fngr'] = 'fngr_fingerprint'
	values['prop_hero']   = bp.account
	values['prop_cost']   = 1000
	values['prop_desc']   = 'CAH desc'
	values['prop_area']   = 'SF'
	values['prop_s_date'] = 'Monday, May 05, 2015 10:00 am'
	values['prop_s_hour'] = ''
	values['prop_s_date'] = 'Monday, May 05, 2015 11:00 am'
	values['prop_f_hour'] = ''

	print 'create appt'
	(proposal, msg) = ht_proposal_create(values, bp)
	return msg


@req_authentication
@ht_server.route("/upload_portfolio", methods=['GET', 'POST'])
def render_multiupload_page():
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('upload_portfolio.html', bp=bp))
	

@req_authentication
@ht_server.route("/edit_portfolio", methods=['GET', 'POST'])
def render_edit_portfolio_page():
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	return make_response(render_template('edit_portfolio.html', bp=bp, portfolio=portfolio))




@req_authentication
@ht_server.route("/disable_reviews", methods=['GET', 'POST'])
def testing_pika_celery_async():
	bp = Profile.get_by_uid(session['uid'])
	five_min = dt.utcnow() + timedelta(minutes=5);
	disable_reviews.apply_async(args=[10], eta=five_min)
	return make_response(jsonify(usrmsg="I'll try."), 200)



@req_authentication
@ht_server.route("/enable_reviews", methods=['GET', 'POST'])
def testing_enable_reviews():
	bp = Profile.get_by_uid(session['uid'])
	prop_uuid = request.values.get('prop');
	proposal=Proposal.get_by_id(prop_uuid)
	enable_reviews(proposal)
	return make_response(jsonify(usrmsg="I'll try."), 200)



@req_authentication
@ht_server.route("/get_threads", methods=['GET', 'POST'])
def get_threads():
	bp = Profile.get_by_uid(session['uid'])
	threads = []

	try:
		threads = db_session.query(UserMessage).filter(UserMessage.msg_parent == None)	\
												.filter(or_(UserMessage.msg_to == bp.prof_id, UserMessage.msg_from == bp.prof_id)).all();

		json_inbox = []
		json_archive = []
		json_messages = [msg.serialize for msg in threads]
		for msg in json_messages:
			profile_to = Profile.get_by_prof_id(msg['msg_to'])
			profile_from = Profile.get_by_prof_id(msg['msg_from'])
			msg['msg_to'] = profile_to.serialize
			msg['msg_from'] = profile_from.serialize
			if (bp == profile_to):
				mbox = json_archive if (msg['msg_flags'] & MSG_STATE_RECV_ARCHIVE) else json_inbox
			elif (bp == profile_from):
				mbox = json_archive if (msg['msg_flags'] & MSG_STATE_SEND_ARCHIVE) else json_inbox
			else:
				print 'wtf'
				continue
			mbox.append(msg)

	except Exception as e:
		print e
		db_session.rollback()

	#(inbox_threads, archived_threads) = ht_assign_msg_threads_to_mbox(bp.prof_id, threads)
	return jsonify(foo=bp.prof_id, inbox=json_inbox, archive=json_archive)



@req_authentication
@ht_server.route("/inbox", methods=['GET', 'POST'])
def render_inbox_page():
	bp = Profile.get_by_uid(session['uid'])
	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')
	threads = []

	try:
		threads = db_session.query(UserMessage, msg_from, msg_to)													\
							 .filter(or_(UserMessage.msg_to == bp.prof_id, UserMessage.msg_from == bp.prof_id))		\
							 .filter(UserMessage.msg_parent == None)												\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)								\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();
		print "threads =", len(threads)
	except Exception as e:
		print e
		db_session.rollback()

	(inbox_threads, archived_threads) = ht_assign_msg_threads_to_mbox(bp.prof_id, threads)
	return make_response(render_template('inbox.html', bp=bp, inbox_threads=inbox_threads, archived_threads=archived_threads))





@req_authentication
@ht_server.route("/inbox/message/<msg_thread>", methods=['GET', 'POST'])
def ht_api_get_message_thread(msg_thread):
	print 'ht_api_get_message_thread: ', msg_thread
	bp = Profile.get_by_uid(session['uid'])

	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')
	thread_messages = []

	try:
		thread_messages = db_session.query(UserMessage, msg_from, msg_to)					\
							 .filter(UserMessage.msg_thread == msg_thread)					\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)		\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();
		print "number of thread_messages", len(thread_messages)
	except Exception as e:
		print e

	msg_zero = filter(lambda msg: (msg.UserMessage.msg_id == msg.UserMessage.msg_thread), thread_messages)[0]
	num_thread_messages = len(thread_messages)

	if (num_thread_messages > 0):
		if (bp.prof_id == msg_zero.UserMessage.msg_from):
			thread_partner_id = msg_zero.UserMessage.msg_to
		else:
			thread_partner_id = msg_zero.UserMessage.msg_from

		thread_partner = Profile.get_by_prof_id(thread_partner_id)
			
		subject = msg_zero.UserMessage.msg_subject
		
		if ((msg_zero.msg_from != bp) and (msg_zero.msg_to != bp)):
			print 'user doesn\'t have access'
			thread_messages = []

	try:
		updated_messages = 0
		for msg in thread_messages:
			if (bp.prof_id == msg.UserMessage.msg_to and msg.UserMessage.msg_opened == None):
				print 'user message never opened before'
				updated_messages = updated_messages + 1
				msg.UserMessage.msg_opened = dt.utcnow();
				msg.UserMessage.msg_flags = (msg.UserMessage.msg_flags | MSG_STATE_LASTMSG_READ)
				db_session.add(msg.UserMessage)
		if (updated_messages > 0):
			print 'committing ' + str(updated_messages) + ' messages'
			db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()


	map(lambda ptr: display_partner_message(ptr, bp.prof_id), thread_messages)
	return make_response(render_template('message.html', bp=bp, num_thread_messages=num_thread_messages, msg_thread_messages=thread_messages, msg_thread=msg_thread, subject=subject, thread_partner=thread_partner))




@req_authentication
@ht_server.route("/message", methods=['GET', 'POST'])
def render_message_page():
	msg_thread_id = request.values.get('msg_thread_id')
	action = request.values.get('action')

	print 'message_thread() ', msg_thread_id, action

	if (action == None):
		return ht_api_get_message_thread(msg_thread_id)
	
	elif (action == "archive"):
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = db_session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
			thread_msg_zero = filter(lambda msg: (msg.msg_id == msg.msg_thread), thread_messages)[0]
			print "msg_thread id and len: ", msg_thread_id, len(thread_messages), thread_msg_zero

			if ((len(thread_messages) > 0) and (thread_msg_zero.msg_from != bp.prof_id) and (thread_msg_zero.msg_to != bp.prof_id)):
				print 'user doesn\'t have access'
				#print 'user', bp.prof_id, 'msg_from == ', thread_msg_zero.msg_from, (thread_msg_zero.msg_from != bp.prof_id)
				#print 'user', bp.prof_id, 'msg_to   == ', thread_msg_zero.msg_to  , (thread_msg_zero.msg_to   != bp.prof_id)
				thread_messages = []

			archive_flag = (thread_msg_zero.msg_to == bp.prof_id) and MSG_STATE_RECV_ARCHIVE or MSG_STATE_SEND_ARCHIVE
			updated_messages = 0
			for msg in thread_messages:
				msg.msg_flags = (msg.msg_flags | archive_flag)
				updated_messages = updated_messages + 1
				db_session.add(msg)

			if (updated_messages > 0):
				print '\"archiving\" ' + str(updated_messages) + " msgs"
				db_session.commit()

			return make_response(jsonify(usrmsg="Message thread archived.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			db_session.rollback()
		return make_response(jsonify(usrmsg="Message thread failed.", next='/inbox'), 500)
	
	elif (action == "restore"):
		print 'restoring msg_thread' + str(msg_thread_id)
		bp = Profile.get_by_uid(session['uid'])
		try:
			thread_messages = db_session.query(UserMessage).filter(UserMessage.msg_thread == msg_thread_id).all();
			thread_msg_zero = filter(lambda msg: (msg.msg_id == msg.msg_thread), thread_messages)[0]
			print "msg_thread id and len: ", msg_thread_id, len(thread_messages), thread_msg_zero

			if ((len(thread_messages) > 0) and (thread_msg_zero.msg_from != bp.prof_id) and (thread_msg_zero.msg_to != bp.prof_id)):
				print 'user doesn\'t have access'
				print 'user', bp.prof_id, 'msg_from == ', thread_msg_zero.msg_from, (thread_msg_zero.msg_from != bp.prof_id)
				print 'user', bp.prof_id, 'msg_to   == ', thread_msg_zero.msg_to  , (thread_msg_zero.msg_to   != bp.prof_id)
				thread_messages = []

			archive_flag = (thread_msg_zero.msg_to == bp.prof_id) and MSG_STATE_RECV_ARCHIVE or MSG_STATE_SEND_ARCHIVE
			updated_messages = 0

			for msg in thread_messages:
				msg.msg_flags = msg.msg_flags & ~archive_flag
				db_session.add(msg)
				updated_messages = updated_messages + 1

			if (updated_messages > 0):
				print '\"restoring\" ' + str(updated_messages) + " msgs"
				db_session.commit()

			return make_response(jsonify(usrmsg="Message thread restored.", next='/inbox'), 200)

		except Exception as e:
			print type(e), e
			db_session.rollback()

		return make_response(jsonify(usrmsg="Message thread restored.", next='/inbox'), 500)	

	# find correct 400 response
	return make_response(jsonify(usrmsg="These are not the message you are looking for.", next='/inbox'), 400)



@req_authentication
@ht_server.route("/compose", methods=['GET', 'POST'])
def render_compose_page():
	hid = request.values.get('hp')
	bp = Profile.get_by_uid(session['uid'])
	hp = None
	next = request.values.get('next')

	if (hid is not None): hp = Profile.get_by_prof_id(hid)
	return make_response(render_template('compose.html', bp=bp, hp=hp, next=next))




@req_authentication
@ht_server.route("/portfolio/<operation>/", methods=['POST'])
def ht_api_update_portfolio(operation):
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])
	print operation

	try:
		# get user's portfolio
		portfolio = db_session.query(Image).filter(Image.img_profile == bp.prof_id).all()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	if (operation == 'add'):
		print 'adding file'
	elif (operation == 'update'):
		print 'usr request: update portfolio'
		images = request.values.get('images')

		try:
			for img in portfolio:
				update = False;
				print img, img.img_id
				jsn = request.values.get(img.img_id)
				if jsn is None:
					print img.img_id, 'doesnt exist in user-set, deleted.'
					db_session.delete(img)
					continue

				obj = json.loads(jsn)
				print img.img_id, obj['idx'], obj['cap']
				if (img.img_order != obj['idx']):
					update = True
					print 'update img_order'
					img.img_order = int(obj['idx'])
				if (img.img_comment != obj['cap']):
					update = True
					print 'update img_cap'
					img.img_comment = obj['cap']

				if (update): db_session.add(img)

			db_session.commit()
		except Exception as e:
			print type(e), e
			db_session.rollback()
			return jsonify(usrmsg='This is embarassing.  We failed'), 500

		return jsonify(usrmsg='Writing a note here: Huge Success'), 200
	else:
		return jsonify(usrmsg='Unknown operation.'), 500

