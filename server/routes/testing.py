
@req_authentication
@insprite_routes.route("/disable_reviews", methods=['GET', 'POST'])
def testing_pika_celery_async():
	bp = Profile.get_by_uid(session['uid'])
	five_min = dt.utcnow() + timedelta(minutes=5);
	disable_reviews.apply_async(args=[10], eta=five_min)
	return make_response(jsonify(usrmsg="I'll try."), 200)



@req_authentication
@insprite_routes.route("/enable_reviews", methods=['GET', 'POST'])
def testing_enable_reviews():
	bp = Profile.get_by_uid(session['uid'])
	prop_uuid = request.values.get('prop');
	proposal=Proposal.get_by_id(prop_uuid)
	enable_reviews(proposal)
	return make_response(jsonify(usrmsg="I'll try."), 200)


@insprite_routes.route("/fakereview/<buyer>/<sellr>", methods=['GET'])
def TESTING_fake_proposal(buyer, sellr):

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

