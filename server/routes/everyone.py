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


from server import database
from server.routes import public_routes	as public
from server.routes import api_routing   as api
from server.models import * 
from server.controllers   import *
from flask.ext.sqlalchemy import Pagination


@public.route('/index.html')
@public.route('/index')
@public.route('/', methods=['GET', 'POST'])
def render_landingpage():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])

	# if user was referred by getsoulcrafting (request.referrer)... then we add a welcome banner.
	referred = True if (request.referrer and 'getsoulcrafting.com' in request.referrer) else None
	return make_response(render_template('index.html', bp=bp, referred=referred))



@public.route('/products/furniture/', methods=['GET', 'POST'])
@public.route('/products/furniture',  methods=['GET', 'POST'])
def render_product_furniture():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('product-furniture.html', bp=bp))



def render_dmca():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('dmca.html', bp=bp))



@public.route('/about/', methods=['GET', 'POST'])
@public.route('/about',  methods=['GET', 'POST'])
def render_about_page():
	bp = None
	if 'uid' in session:
		bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('about.html', bp=bp))



@public.route('/terms/', 		  methods=['GET'])
@public.route('/terms', 		  methods=['GET'])
@public.route('/terms/service', methods=['GET'])
def render_terms_service_page():
	bp = None
	if 'uid' in session: bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('terms-service.html', bp=bp))



@public.route('/terms/privacy', methods=['GET'])
def render_terms_privacy_page():
	bp = None
	if 'uid' in session: bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('terms-privacy.html', bp=bp))



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
		database.session.rollback()

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




@public.route('/email/<operation>/<data>/', methods=['GET','POST'])
@public.route('/email/<operation>/<data>',  methods=['GET','POST'])
def sc_email_operations(operation, data):
	print "sc_email_operations: begin", operation
	print "sc_email_operations: data: ", data
	if (operation == 'verify'):
		email = request.values.get('email')
		print 'sc_email_operations: verify: data  = ', data, 'email =', email

		account = Account.authorize_with_hashcode(email, data)
		if (not account):
			session['messages'] = "Verification code and email address did not match what is on file."
			return redirect('/signin')

		# bind session cookie to this user's profile
		profile = Profile.get_by_uid(account.userid)
		bind_session(account, profile)
		return redirect('/profile')


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




#@public.route("/share/", methods=['GET', 'POST'])
#@public.route("/share",	methods=['GET', 'POST'])
def render_share_page():
	print 'render_share_page()'
	back = request.values.get('back')
	pp(request.args)
	for idx in request.args: print idx, request.values.get (idx)
	return make_response(render_template('share.html', back=back))



@sc_server.csrf.exempt
@api.route("/share/email", methods=['POST'])
def api_share_via_email():
	fragment	= render_template('fragments/share-email.html')
	resp_code	= 200
	resp_mesg	= 'Done'
	return make_response(jsonify(sc_msg=resp_mesg, embed=fragment), resp_code)
