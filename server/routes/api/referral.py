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


from server import sc_server
from server.models import *
from server.routes import api_routing as api
from server.routes import test_routes as test
from server.routes import public_routes as public
from server.routes.helpers import *
from server.controllers import *


@public.route('/referral/', methods=['GET'])
@public.route('/referral',  methods=['GET'])
def render_create_referral_page():
	bp = Profile.get_by_uid(session.get('uid'))
	rf = ReferralForm(request.values)
	return make_response(render_template('referral.html', bp=bp, form=rf))



@api.route('/referral/create/', methods=['POST'])
@api.route('/referral/create',  methods=['POST'])
@sc_authenticated
def api_referral_create():
	print 'api_referral_create(): enter'
	profile	= Profile.get_by_uid(session.get('uid'))
	rf = ReferralForm(request.form)
	bus_id	= rf.bid.data
	ref_id	= rf.rid.data
	context	= rf.context.data
	content = rf.content.data

	if not rf.validate_on_submit():
		print rf.errors
		return make_response(jsonify(rf.errors), 400)

	try:
		# business may not exist.
		business = Business.get_by_id(bus_id)
		if (not business):
			print 'business doesn\'t exist - import it.'
			business = Business.import_from_json(bus_id)

		context = ','.join([ x.strip().lower() for x in context.split(',') ])
		referral = Referral(business.bus_id, profile, content, context)
		database.session.add(referral)
		database.session.commit()

		session_referrals = session.get('referrals', {})
		session_referrals[referral.ref_uuid] = referral
		session['referrals'] = session_referrals
		return make_response(jsonify(referral.serialize), 200)
	except Exception as e:
		print type(e), e
		database.session.rollback()
	return e.api_response(request.method)



@api.route('/referral/<string:ref_id>/', methods=['GET'])
@api.route('/referral/<string:ref_id>',  methods=['GET'])
def api_referral_read(ref_id):
	print 'api_referral_read: enter'
	referral = Referral.get_by_refid(ref_id)
	editmode = request.args.get('edit')
	if (not referral): return make_response(jsonify(referral='missing resource'), 400)

	bp = Profile.get_by_uid(session.get('uid'))

	# request to update referral, must be owner
	if (editmode and referral.authored_by(bp)):
		print 'bp authored referral'
		rf = ReferralForm(request.values)
		rf.bid.data = referral.ref_business
		rf.bid.data = referral.ref_uuid
		rf.content.data	= referral.ref_content
		rf.context.data	= referral.ref_project
		return make_response(render_template('referral.html', bp=bp, form=rf))

	# the BP did not author referral and should not edit referral.
	return make_response(jsonify(referral=referral.serialize), 200)



@sc_server.csrf.exempt
@api.route('/referral/<string:ref_id>/update/', methods=['POST'])
@api.route('/referral/<string:ref_id>/update',	methods=['POST'])
def api_referral_update(ref_id):
	referral	= Referral.get_by_refid(ref_id)

	rf = ReferralForm(request.form)
	bus_id	= rf.bid.data
	context	= rf.context.data
	content = rf.content.data

	if (not referral): return make_response(jsonify(request='missing valid resource'), 400)
	referral.ref_business	= bus_id
	referral.ref_content	= content
	referral.ref_project	= ','.join([ x.strip().lower() for x in context.split(',') ])

	try:
		database.session.add(referral)
		database.session.commit()
	except Exception as e:
		database.session.rollback()
		print type(e), e
		return e.api_response(request.method)
	return make_response(jsonify(referral.serialize), 200)



@sc_server.csrf.exempt
@api.route('/referral/<string:ref_id>/destroy/', methods=['DELETE'])
@api.route('/referral/<string:ref_id>/destroy',  methods=['DELETE'])
def api_referral_destroy(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): return make_response(jsonify(referral='missing resource'), 400)

	return make_response(jsonify(referral='destroyed'), 200)



#################################################################################
### TEST ROUTES #################################################################
#################################################################################

@test.route('/referral/<string:ref_id>/valid/',	methods=['GET','POST'])
@test.route('/referral/<string:ref_id>/valid',	methods=['GET','POST'])
def test_reflist_valid(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): return make_response(jsonify(referral='missing resource'), 400)

	referral.set_valid()
	return make_response(jsonify(flags=referral.ref_flags), 200)
	return make_response(jsonify(referral.serialize), 200)


@test.route('/referral/<string:ref_id>/invalid/',	methods=['GET','POST'])
@test.route('/referral/<string:ref_id>/invalid',	methods=['GET','POST'])
def test_reflist_setinvalid(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): return make_response(jsonify(referral='missing resource'), 400)

	referral.set_invalid()
	flags = referral.serialize['ref_flags']
	return make_response(jsonify(flags=referral.ref_flags), 200)
	return make_response(jsonify(referral=referral.ref_flags), 200)
