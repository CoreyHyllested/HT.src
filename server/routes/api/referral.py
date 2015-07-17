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
	invite = InviteForm(request.form)
	return make_response(render_template('referral.html', bp=bp, form=invite))



@api.route('/referral/<string:ref_id>/', methods=['POST'])
@api.route('/referral/<string:ref_id>',  methods=['POST'])
def api_referral_view(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): return make_response(jsonify(referral='missing resource'), 400)

	return make_response(jsonify(referral=referral.serialize), 200)



@sc_server.csrf.exempt
@api.route('/referral/create', methods=['POST'])
def api_referral_create():
	print 'api_referral_create(): enter'
	bus_id	= request.values.get('business')
	ref_id	= request.values.get('referral')
	content = request.values.get('content')
	project = request.values.get('projects')

#	if form.validate_on_submit():
	if (bus_id and content):
		try:
			# business may not exist.
			business = Business.get_by_id(bus_id)
			if (not business):
				print 'business doesn\'t exist - import it.'
				business = Business.import_from_json(bus_id)

			projects = ','.join([ x.strip().lower() for x in request.values.get('projects').split(',') ])
			referral = Referral(business.bus_id, content, projects)
			database.session.add(referral)
			database.session.commit()

			session_referrals = session.get('referrals', {})
			session_referrals[referral.ref_uuid] = referral
			session['referrals'] = session_referrals
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return e.api_response(request.method)
		return make_response(jsonify(referral.serialize), 200)

	missing = ''
	if not (profile): missing = missing + ' (profile) '
	if not (content): missing = missing + ' (content) '
	return make_response(jsonify(missing=missing), 400)



@sc_server.csrf.exempt
@api.route('/referral/<string:ref_id>/update/', methods=['POST'])
@api.route('/referral/<string:ref_id>/update',	methods=['POST'])
def api_referral_update(ref_id):
	referral	= Referral.get_by_refid(ref_id)
	bus_id	= request.values.get('business')
	content = request.values.get('content')
	project = request.values.get('projects')

	if (not referral): return make_response(jsonify(request='missing valid resource'), 400)
	referral.ref_business	= bus_id
	referral.ref_content	= content
	referral.ref_project	= ','.join([ x.strip().lower() for x in project.split(',') ])

	try:
		database.session.add(referral)
		database.session.commit()
	except Exception as e:
		database.session.rollback()
		print type(e), e
		return e.api_response(request.method)

	return make_response(jsonify(referral.serialize), 200)




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

