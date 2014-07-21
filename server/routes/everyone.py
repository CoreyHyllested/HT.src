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
from flask import render_template, make_response, session, request, redirect
from flask.ext.sqlalchemy import Pagination
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models import * 
from server.controllers import *
from server.forms import NewPasswordForm, NTSForm, SearchForm, RecoverPasswordForm
from server import ht_csrf


@insprite_views.route('/index')
@insprite_views.route('/', methods=['GET', 'POST'])
def render_landingpage():
	""" Returns the HeroTime front page for users and Heros
		- detect HT Session info.  Provide modified info.
	"""
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('index.html', bp=bp))



@ht_csrf.exempt
@insprite_views.route('/profile', methods=['GET', 'POST'])
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
		profile_imgs = db_session.query(Image).filter(Image.img_profile == hp.prof_id).all()
		hp_c_reviews = htdb_get_composite_reviews(hp)
	except Exception as e:
		print e
		db_session.rollback()

	visible_imgs = ht_filter_images(profile_imgs, 'VISIBLE', dump=False)
	hero_reviews = ht_filter_composite_reviews(hp_c_reviews, 'REVIEWED', hp, dump=False)
	show_reviews = ht_filter_composite_reviews(hero_reviews, 'VISIBLE', None, dump=False)	#visible means displayable.
	return make_response(render_template('profile.html', title='- ' + hp.prof_name, hp=hp, bp=bp, reviews=show_reviews, portfolio=visible_imgs))




@insprite_views.route('/terms', methods=['GET'])
def render_terms_of_service():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('tos.html', title = '- Terms and Conditions', bp=bp))




@insprite_views.route("/dmca", methods=['GET', 'POST'])
def render_dmca():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('dmca.html', bp=bp))




@insprite_views.route("/about", methods=['GET', 'POST'])
def render_about_page():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('about.html', bp=bp))




@ht_csrf.exempt
@insprite_views.route('/search',  methods=['GET', 'POST'])
@insprite_views.route('/search/<int:page>',  methods=['GET', 'POST'])
def render_search(page = 1):
	""" Provides ability to everyone to search for Heros.  """
	bp = None

	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# get all the search 'keywords'
	#for key in request.values:
	#	print key, '=', request.values.get(key)

	keywords = request.values.get('keywords_field')
	industry = request.values.get('industry_field', -1, type=int)
	rateFrom = request.values.get('rate_from_field', 0, type=int)
	rateTo =   request.values.get('rate_to_field', 9999, type=int)
	form = SearchForm(request.form)

	if (rateTo < rateFrom):
		rate_temp	= rateTo
		rateTo		= rateFrom
		rateFrom	= rate_temp

	try:
		results = db_session.query(Profile) #.order_by(Profile.created)
		results_industry = results #.all();
		print 'Total Profiles:', len(results.all())
		if (industry != -1):
			industry_str = Industry.industries[industry]
			results_industry = results.filter(Profile.industry == industry_str)
			print '\tProfiles in ', Industry.industries[industry], 'industry =', len(results_industry.all())
			for profile in results_industry.all(): print '\t\t' + str(profile)
			
		results_rate = results.filter(Profile.prof_rate.between(rateFrom, rateTo))
		print '\tProfiles w rates between $' + str(rateFrom) + ' - $' + str(rateTo) + ':', len(results_rate.all())
				
		if (keywords is not None):
			print "keywords = ", keywords
			results_name = results.filter(Profile.prof_name.ilike("%"+keywords+"%"))
			print 'results for name', len(results_name.all())
			results_desc = results.filter(Profile.prof_bio.ilike("%"+keywords+"%"))
			print 'results for desc', len(results_desc.all())
			rc_hdln = results.filter(Profile.headline.ilike("%"+keywords+"%"))
			print 'results for hdln', len(rc_hdln.all())

			print len(results_name.all()), len(rc_hdln.all()), len(results_desc.all())
	
			# filter by location, use IP as a tell
			rc_keys = results_desc.union(rc_hdln).union(results_name) #.all() #paginate(page, 4, False)
			#rc_keys = results_desc.union(rc_hdln).union(results_name).all() #.intersect(results_industry).all() #paginate(page, 4, False)
		else:
			print 'returning all all'
			rc_keys = results #.all() #(page, 4, False)

		q_rc = rc_keys.intersect(results_rate).intersect(results_industry).order_by(Profile.created)
	except Exception as e:
		print e
		db_session.rollback()

	page_items = []
	page_total = []
	total_results = q_rc.all();
	per_page = 3
	trc_start_pg = (page - 1) * per_page
	trc_end_pg = (page * per_page)
	if (trc_start_pg) > (len(total_results)):
		trc_start_pg = len(total_results) - per_page
	if (trc_end_pg > (len(total_results))):
		trc_end_pg = len(total_results)
	new_results = total_results[trc_start_pg:trc_end_pg]
	paginate = Pagination(q_rc, page, per_page=3, total=page_total, items=q_rc.all())
	print 'page_items', page_items
	print 'page_total', page_total
	print 'page_heros', paginate.items

	return make_response(render_template('search.html', bp=bp, form=form, rc_heroes=len(new_results), heroes=new_results))




@insprite_views.route("/password/recover", methods=['GET', 'POST'])
def render_password_reset_request():
	form = RecoverPasswordForm(request.form)
	usrmsg = None
	if request.method == 'POST':
		print 'password_reset_request() -', form.rec_input_email.data
		usrmsg = ht_password_recovery(form.rec_input_email.data)
		# TODO on success... AJAX respond with message.  After 10 seconds, redirect user.
		return make_response(redirect(url_for('insprite.render_login')))
	return render_template('recovery.html', form=form, errmsg=usrmsg)




@insprite_views.route('/password/reset/<challengeHash>', methods=['GET', 'POST'])
def render_password_reset_page(challengeHash):
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
			ht_send_password_changed_confirmation(email)
		except Exception as e:
			trace(str(e))
			db_session.rollback()
		return redirect('/login')

	elif request.method == 'POST':
		trace("POST New password isn't valid " + str(form.errors))

	return render_template('newpassword.html', form=form)



# related to authentication
@insprite_views.route("/email/<operation>/<data>", methods=['GET','POST'])
def ht_email_operations(operation, data):
	print operation, data
	if (operation == 'verify'):
		email = request.values.get('email')
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
	return jsonify(bug=400), 400 #pageNotFound('Not sure what you were looking for')




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
		ht_send_verify_email_address(email, profile.prof_name, challenge_hash)



################################################################################
### HELP FUNCTIONS.  ###########################################################
################################################################################


