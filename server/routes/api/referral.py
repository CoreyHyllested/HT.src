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



#################################################################################
### PUBLIC ROUTES ###############################################################
#################################################################################

@public.route('/referral/', methods=['GET'])
@public.route('/referral',  methods=['GET'])
def render_create_referral_page():
	bp = Profile.get_by_uid(session.get('uid'))
	rf = ReferralForm(request.values)
	return make_response(render_template('referral.html', bp=bp, form=rf))



@public.route('/referral/<string:ref_id>/', methods=['GET'])
@public.route('/referral/<string:ref_id>',  methods=['GET'])
def render_referral(ref_id):
	print 'render_referral(%s)', ref_id
	try:
		composite = Referral.get_composite_referral_by_id(ref_id)
		if (not composite): raise NoReferralFound(ref_id)

		bp = Profile.get_by_uid(session.get('uid'))
		editmode = request.args.get('edit')

		# [SECURITY] request to update referral, ensure bp authored the referral
		#if (not composite.referral.authored_by(bp))
		if (not (request.args.get('edit') and (bp and bp.prof_id == composite.Referral.ref_profile))):
			editmode=False

		# populate Referral's form data.
		rf = ReferralForm(request.values)
		rf.bid.data = composite.Referral.ref_business
		rf.rid.data = composite.Referral.ref_uuid
		rf.content.data	= composite.Referral.ref_content
		rf.context.data	= composite.Referral.ref_project
		rf.trusted.data = composite.business.bus_name

		if (composite.display_addr): rf.trusted.data = rf.trusted.data + ' | ' + composite.display_addr
		return make_response(render_template('referral.html', bp=bp, form=rf, edit=editmode))
	except SanitizedException as e:
		return e.response()





#################################################################################
### API / DATA ROUTES ###########################################################
#################################################################################

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

	try:
		if not rf.validate_on_submit():
			raise InvalidInput(errors=rf.errors)

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
	except SanitizedException as e:
		return e.response()
	except Exception as e:
		# IntegrityError (db error)
		database.session.rollback()
		e = SanitizedException(e, status='Oops. An error occurred', code=500)
		print type(e.exception()), str(e.exception())
		return e.response()



@sc_server.csrf.exempt
@api.route('/referral/<string:ref_id>/', methods=['POST'])
@api.route('/referral/<string:ref_id>',  methods=['POST'])
def api_referral_read(ref_id):
	print 'api_referral_read: enter'
	composite = Referral.get_composite_referral_by_id(ref_id)
	try:
		if (not composite): raise NoReferralFound(ref_id)
		return make_response(jsonify(referral=composite.Referral.serialize), 200)
	except SanitizedException as e:
		return e.response()




@api.route('/referral/<string:ref_id>/update/', methods=['POST'])
@api.route('/referral/<string:ref_id>/update',	methods=['POST'])
@sc_authenticated
def api_referral_update(ref_id):
	bp = Profile.get_by_uid(session.get('uid'))
	referral	= Referral.get_by_refid(ref_id)

	rf = ReferralForm(request.form)
	bus_id	= rf.bid.data
	context	= rf.context.data
	content = rf.content.data

	try:
		if (not referral): raise NoReferralFound(ref_id)
		if (not rf.validate_on_submit()):	raise InvalidInput(errors=rf.errors)
		if (not referral.authored_by(bp)):	raise SanitizedException('Permission Error', 'You do not have permission to modify this resource', code=401)
		referral.ref_business	= bus_id
		referral.ref_content	= content
		referral.ref_project	= ','.join([ x.strip().lower() for x in context.split(',') ])

		database.session.add(referral)
		database.session.commit()
		return make_response(jsonify(referral.serialize), 200)
	except InvalidInput as e:
#		Intent here is to provide feedback;
#		Currently, failing, to set red-border or showing message because TT-updates DOM
#		if (e.errors().get('context')):
#			e.status(e.errors()['context'])
		return e.response()
	except SanitizedException as e:
		return e.response()
	except Exception as e:
		database.session.rollback()
		e = SanitizedException(e, status='Oops. An error occurred', code=500)
		print type(e.exception()), str(e.exception())
		return e.response()




@sc_server.csrf.exempt
@api.route('/referral/<string:ref_id>/destroy/', methods=['DELETE'])
@api.route('/referral/<string:ref_id>/destroy',  methods=['DELETE'])
def api_referral_destroy(ref_id):
	bp = Profile.get_by_uid(session.get('uid'))
	referral = Referral.get_by_refid(ref_id)

	try:
		if (not referral): raise NoReferralFound(ref_id)
		if (not referral.authored_by(bp)): raise SanitizedException('Permission Error', 'You do not have permission to modify this resource', code=401)

		database.session.delete(referral)
		database.session.commit()
	except SanitizedException as e:
		return e.response()
	except Exception as e:
		database.session.rollback()
		e = SanitizedException(e, status='Oops. An error occurred', code=500)
		print type(e.exception()), str(e.exception())
		return e.response()
	return make_response(jsonify(referral='destroyed'), 200)





#################################################################################
### TEST ROUTES #################################################################
#################################################################################


@test.route('/referral/<string:ref_id>/valid/',	methods=['GET','POST'])
@test.route('/referral/<string:ref_id>/valid',	methods=['GET','POST'])
def test_reflist_valid(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): raise NoReferralFound(ref_id)

	referral.set_valid()
	return make_response(jsonify(flags=referral.ref_flags, referral=referral.serialize), 200)


@test.route('/referral/<string:ref_id>/invalid/',	methods=['GET','POST'])
@test.route('/referral/<string:ref_id>/invalid',	methods=['GET','POST'])
def test_reflist_setinvalid(ref_id):
	referral = Referral.get_by_refid(ref_id)
	if (not referral): raise NoReferralFound(ref_id)

	referral.set_invalid()
	flags = referral.serialize['ref_flags']
	return make_response(jsonify(flags=referral.ref_flags, referral=referral.serialize), 200)

