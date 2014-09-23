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
from server.models import * 
from server.controllers import *
from server.forms import NewPasswordForm, ProposalForm, SearchForm, RecoverPasswordForm
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
				return redirect('/login')	
			hp = bp

		# replace 'hp' with the actual Hero's Profile.
		print "HP = ", hp.prof_name, hp.prof_id, hp.account
	except Exception as e:
		print e
		return jsonify(usrmsg='Sorry, bucko, couldn\'t find who you were looking for'), 500

	try:
		# complicated search queries can fail and lock up DB.
		profile_imgs = db_session.query(Image).filter(Image.img_profile == hp.prof_id).all()
		hp_c_reviews = htdb_get_composite_reviews(hp)
		hp_lessons = ht_get_active_lessons(hp)
		avail = Availability.get_by_prof_id(hp.prof_id)	
	except Exception as e:
		print type(e), e
		db_session.rollback()


	visible_imgs = ht_filter_images(profile_imgs, 'VISIBLE', dump=False)
	hero_reviews = ht_filter_composite_reviews(hp_c_reviews, 'REVIEWED', hp, dump=False)
	show_reviews = ht_filter_composite_reviews(hero_reviews, 'VISIBLE', None, dump=False)	#visible means displayable.
	return make_response(render_template('profile.html', title='- ' + hp.prof_name, hp=hp, bp=bp, reviews=show_reviews, lessons=hp_lessons, portfolio=visible_imgs, avail=avail))




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
	""" Provides ability to find Mentors. """
	bp = None

	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# show all the 'keywords'
	#for key in request.values:
	#	print key, '=', request.values.get(key)

	find_keywords = request.values.get('keywords_field')
	#find_industry = request.values.get('industry_field', -1, type=int)
	find_rateFrom = request.values.get('rate_from_field', 0, type=int)
	find_rateTo =   request.values.get('rate_to_field', 9999, type=int)
	form = SearchForm(request.form)

	if (find_rateTo < find_rateFrom):
		tmp				= find_rateTo
		find_rateTo		= find_rateFrom
		find_rateFrom	= tmp

	try:
		# find all mentor profiles
		mentors = db_session.query(Profile)										\
							.filter(Profile.availability > PROF_MENTOR_NONE) 	\
							.filter(Profile.prof_rate.between(find_rateFrom, find_rateTo))
							#.order_by(Profile.created)
		all_mentors = mentors.all()
		print '\tMentors matching rates between $' + str(find_rateFrom) + ' - $' + str(find_rateTo) + ':', len(all_mentors)

		#results_industry = mentors #.all();
		#if (find_industry != -1):
		#	industry_str = Industry.industries[find_industry]
		#	results_industry = mentors.filter(Profile.industry == industry_str)
		#	print '\tProfiles in ', Industry.industries[find_industry], 'industry =', len(results_industry.all())
		#	for profile in results_industry.all(): print '\t\t' + str(profile)


		for mentor in all_mentors:
			print mentor
			for lesson in mentor.lessons:
				print mentor, lesson
#				match_l_name = lesson.filter(Lesson.lesson_title.ilike('%'+find_keywords+'%'))
#				match_l_desc = lesson.filter(Lesson.lesson_description.ilike('%'+find_keywords+'%'))
#				print 'results for lesson name', len(match_l_name) + ', desc', len(match_l_desc)

		if (find_keywords is not None):
			print "keywords = ", str(find_keywords)
			matched_name = mentors.filter(Profile.prof_name.ilike("%"+find_keywords+"%"))
			matched_hdln = mentors.filter(Profile.headline.ilike("%"+find_keywords+"%"))
			matched_bio  = mentors.filter(Profile.prof_bio.ilike("%"+find_keywords+"%"))
			print 'results for name', str(len(matched_name.all())) + ', headline', str(len(matched_hdln.all())) + ', bio', str(len(matched_bio.all()))

			# filter by location, use IP as a tell
			matched_prof = matched_bio.union(matched_hdln).union(matched_name) #.all() #paginate(page, 4, False)
			#matched_prof = matched_bio.union(matched_hdln).union(matched_name).all() #.intersect(results_industry).all() #paginate(page, 4, False)
		else:
			print 'returning all mentors'
			matched_prof = mentors #.all() #(page, 4, False)

		matched_results = matched_prof.order_by(Profile.created)
		#matched_results = matched_prof.intersect(results_industry).order_by(Profile.created)
	except Exception as e:
		print e
		db_session.rollback()

	total_results = matched_results.all();
	PER_PAGE = 10
	start_pg = (page - 1) * PER_PAGE
	end_pg = (page * PER_PAGE)
	if (start_pg) > (len(total_results)):
		start_pg = len(total_results) - PER_PAGE
	if (end_pg > (len(total_results))):
		end_pg = len(total_results)
	page_mentors = total_results[start_pg:end_pg]

	#page_items = []
	#page_total = []
	#paginate = Pagination(matched_results, page, per_page=PER_PAGE, total=page_total, items=matched_results.all())
	#print 'page_items', page_items
	#print 'page_total', page_total
	#print 'page_heros', paginate.items

	return make_response(render_template('search.html', bp=bp, form=form, rc_heroes=len(page_mentors), heroes=page_mentors))




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
	print "ht_email_operations: begin"
	print "ht_email_operations: operation: ", operation
	print "ht_email_operations: data: ", data
	if (operation == 'verify'):
		email = request.values.get('email')
		nexturl = request.values.get('next_url')
		print 'ht_email_operations: verify: data  = ', data, 'email =', email, "nexturl =", nexturl
		return ht_email_verify(email, data, nexturl)
	elif (operation == 'request-response'):
		nexturl = request.values.get('nexturl')
		return make_response(render_template('verify_email.html', nexturl=nexturl))
	elif (operation == 'request-verification') and ('uid' in session):

		profile = Profile.get_by_uid(session.get('uid'))
		account = Account.get_by_uid(session.get('uid'))
		email_set = set([account.email, request.values.get('email_addr')])
		print email_set

		ht_send_verification_to_list(account, email_set)
		return jsonify(rc=200), 200
	return jsonify(bug=400), 400 #pageNotFound('Not sure what you were looking for')




def ht_send_verification_to_list(account, email_set):
	print 'ht_send_verification_to_list() enter'
	try:
		account.reset_security_question()
		db_session.add(account)
		db_session.commit()
	except Exception as e:
		print type(e), e
		db_session.rollback()

	for email in email_set:
		print 'sending email to', email
		ht_send_email_address_verify_link(email, account)



################################################################################
### HELP FUNCTIONS.  ###########################################################
################################################################################


