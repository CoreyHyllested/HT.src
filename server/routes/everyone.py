#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from . import sc_ebody
from flask import render_template, make_response, redirect
from flask import session, request
from flask.ext.sqlalchemy import Pagination
from server.infrastructure.srvc_database import db_session
from server.models import * 
from server.controllers import *
from server.forms import NewPasswordForm, SearchForm
from server.forms import GiftForm, RecoverPasswordForm
from server import sc_csrf
from pprint import pprint


@sc_ebody.route('/index.html')
@sc_ebody.route('/index')
@sc_ebody.route('/', methods=['GET', 'POST'])
def render_landingpage():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# if user was referred by getsoulcrafting (request.referrer)... then we add a welcome banner.
	referred = True if (request.referrer and 'getsoulcrafting.com' in request.referrer) else None
	return make_response(render_template('index.html', bp=bp, referred=referred))



@sc_ebody.route("/purchase", methods=['GET', 'POST'])
def render_purchase_page_ebody():
	bp = None
	if (session.get('uid') is not None):
		bp = Profile.get_by_uid(session.get('uid'))

	gift = GiftForm(request.form)
	return make_response(render_template('purchase.html', bp=bp, form=gift, STRIPE_PK=ht_server.config['STRIPE_PUBLIC']))


@sc_ebody.route('/gift/<gift_id>', methods=['GET', 'POST'])
def render_giftpage(gift_id):
	print 'render_gift(): enter [' + str(gift_id) + ']'
	bp = None
	if (session.get('uid') is not None):
		bp = Profile.get_by_uid(session.get('uid'))


	if (gift_id):
		print 'render_gift(): getting gift [' + str(gift_id) + ']'
		gift = GiftCertificate.get_by_giftid(gift_id)

	if ((gift is None) or (gift_id is None)):
		#raise 'Gift Not Found' #GiftNotFoundError(from_user)
		return make_response("Gift Not Found", 500)


	# Was this a referral?  If so, set ref=ref_id
	referral = Referral.get_by_gift_id(gift_id)
	ref_id = (referral.ref_id) if (referral) else None
	#print gift
	#print referral
	#if (referral):
	#	prof_referral = Profile.get_by_uid(referral.ref_account)	#

	print 'render_gift(): render page'
	return make_response(render_template('gift.html', bp=bp, gift=gift, referral=ref_id))



#@sc_csrf.exempt
#@insprite_views.route('/profile', methods=['GET', 'POST'])
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




#@insprite_views.route('/terms/service', methods=['GET'])
def render_terms_of_service():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('tos.html', title = '- Terms and Conditions', bp=bp))




#@insprite_views.route("/dmca", methods=['GET', 'POST'])
def render_dmca():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('dmca.html', bp=bp))




#@sc_ebody.route("/about", methods=['GET', 'POST'])
def render_about_page():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('about.html', bp=bp))


@sc_ebody.route('/about/version', methods=['GET'])
def render_about_version_page():
	return render_template('version')








#@sc_csrf.exempt
#@insprite_views.route('/search',  methods=['GET', 'POST'])
#@insprite_views.route('/search/<int:page>',  methods=['GET', 'POST'])
def render_search(page = 1):
	""" Provides ability to find Mentors. """
	bp = None

	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# show all the 'keywords'
	#for key in request.values:
	#	print key, '=', request.values.get(key)

	find_keywords = request.values.get('keywords_field', '').split()
	#find_industry = request.values.get('industry_field', -1, type=int)
	find_cost_min = request.values.get('rate_from_field', 0, type=int)
	find_cost_max = request.values.get('rate_to_field', 9999, type=int)
	form = SearchForm(request.form)

	if (find_cost_max < find_cost_min):
		tmp				= find_cost_max
		find_cost_max	= find_cost_min
		find_cost_min	= tmp

		#results_industry = mentors #.all();
		#if (find_industry != -1):
		#	industry_str = Industry.industries[find_industry]
		#	results_industry = mentors.filter(Profile.industry == industry_str)
		#	print '\tProfiles in ', Industry.industries[find_industry], 'industry =', len(results_industry.all())

#		if (find_keywords is not None):
#			print "keywords = ", str(find_keywords)
#			matched_name = mentors.filter(Profile.prof_name.ilike("%"+find_keywords+"%"))
#			match_l_desc = lessons.filter(Lesson.lesson_description.ilike('%'+find_keywords+'%'))
#			print 'results for name', str(len(matched_name.all())) + ', headline', str(len(matched_hdln.all())) + ', bio', str(len(matched_bio.all()))
#			print 'results for lesson name', str(len(match_l_name.all())) + ', desc', str(len(match_l_desc.all()))

			# filter by location, use IP as a tell
#			matched_prof = matched_bio.union(matched_hdln).union(matched_name) #.all() #paginate(page, 4, False)
			#matched_prof = matched_bio.union(matched_hdln).union(matched_name).all() #.intersect(results_industry).all() #paginate(page, 4, False)
#		else:
#			print 'returning all mentors'
#			matched_prof = mentors #.all() #(page, 4, False)
#		matched_results = matched_prof.intersect(results_industry).order_by(Profile.created)

	try:
		total_results = htdb_search_mentors_and_lessons(find_keywords, find_cost_min, find_cost_max)
	except Exception as e:
		print e, type(e)
		db_session.rollback()

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

	return make_response(render_template('search.html', bp=bp, form=form, mentors=page_mentors))




@sc_ebody.route("/password/recover", methods=['GET', 'POST'])
def render_password_reset_request(sc_msg=None):
	form = RecoverPasswordForm(request.form)
	if form.validate_on_submit():
		print 'password_reset_request() -', form.email.data
		try:
			sc_password_recovery(form.email.data)
			session['messages'] = "Reset instructions were sent."
			return make_response(redirect(url_for('sc_ebody.render_login')))
		except NoEmailFound as nef:
			sc_msg = nef.sanitized_msg()
		except AccountError as ae:
			sc_msg = ae.sanitized_msg()
			print ae
	return render_template('password_recover.html', form=form, sc_alert=sc_msg)




@sc_ebody.route('/password/reset/<challengeHash>', methods=['GET', 'POST'])
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
			return redirect('/login')

	if form.validate_on_submit():
		account = accounts[0]
		account.set_sec_question("")
		account.pwhash = generate_password_hash(form.rec_input_newpass.data)
		trace("hash " + account.pwhash)

		try:
			db_session.add(account)
			db_session.commit()
			sc_send_password_changed_confirmation(email)
		except Exception as e:
			trace(type(e) + ' ' + str(e))
			db_session.rollback()
		return redirect('/login')
	elif request.method == 'POST':
		trace("POST New password isn't valid " + str(form.errors))
	return render_template('password_reset.html', form=form)



@sc_ebody.route("/share/", methods=['GET', 'POST'])
@sc_ebody.route("/share",	 methods=['GET', 'POST'])
def render_share_page():
	back = request.values.get('back')
	print 'render_share_page()'
	pprint(request.args)
	for idx in request.args:
		print idx, request.values.get (idx)

	return make_response(render_template('share.html', back=back))




@sc_ebody.route("/email/<operation>/<data>", methods=['GET','POST'])
def sc_email_operations(operation, data):
	print "sc_email_operations: begin", operation
	print "sc_email_operations: data: ", data
	if (operation == 'verify'):
		email = request.values.get('email')
		nexturl = request.values.get('next_url')
		print 'sc_email_operations: verify: data  = ', data, 'email =', email, "nexturl =", nexturl
		return sc_email_verify(email, data, nexturl)
#	elif (operation == 'share'):
#		print "sc_email_operations: you've chosen wisely.... share: "
#		msg_to	 = request.values.get('recipient')
#		msg_sub	 = request.values.get('subject')
#		msg_body = request.values.get('composeBody')
#		ht_send_share_email(msg_to, msg_sub, msg_body)
#		return jsonify(rc=200, whatwhat='yeah, that\'s the shit I\'m talking about'), 200
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
