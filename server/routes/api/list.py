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
from server.routes.helpers import *
from server.controllers import *


@api.route('/list/<string:list_id>/', methods=['GET'])
@api.route('/list/<string:list_id>',  methods=['GET'])
def api_reflist_view(list_id):
	reflist = RefList.get_by_listid(list_id)
	if (not reflist): return make_response(jsonify(list='missing resource'), 400)

	return make_response(jsonify(list=reflist.serialize), 200)


@sc_server.csrf.exempt
@api.route('/list/create', methods=['POST'])
def api_reflist_create():
	print 'api_reflist_create(): enter'
	profile	= request.values.get('profile')
	project = request.values.get('project')
	name	= request.values.get('name')
	desc	= request.values.get('desc')

	if (profile):
		try:
			# require project here?
			reflist = RefList(profile, project, name, desc)
			database.session.add(reflist)

			session_lists = session.get('lists', {})
			session_lists[reflist.list_uuid] = reflist
			session['lists'] = session_lists
			for x in session_lists: pp(x)
		except SanitizedException as e:
			database.session.rollback()
			print type(e), e
			return e.response()
		return make_response(jsonify(created=reflist.serialize), 200)
	missing = []
	if (not profile): missing.append('profile')
	if (not project): missing.append('project')

	return make_response(jsonify(missing=missing), 400)


@sc_server.csrf.exempt
@api.route('/list/<string:list_id>/update/', methods=['POST'])
@api.route('/list/<string:list_id>/update',  methods=['POST'])
def api_reflist_update(list_id):
	reflist = RefList.get_by_listid(list_id)
	profile = Profile.get_by_uid(session.get('uid'))
	ref_op	= request.values.get('operation')
	ref_id	= request.values.get('referral')
	if (not ref_op):	raise NoResourceFound('List Operation', ref_op)

	if (ref_op == 'ADD_REFERRAL'):
		print 'Add referal operation'
		referral = Referral.get_by_refid(ref_id)

		try:
			if (not reflist):	raise NoResourceFound('reflist', list_id)
			if (not profile):	raise NoProfileFound(session.get('uid'))
			# checking permissions
			if not reflist.profile_can_modify(profile): raise SanitizedException('Permission Error', 'You do not have permission to modify this resource', code=401)
			if (not referral):	raise NoReferralFound(ref_id)

			rc = reflist.add_referral(referral)
			if (rc): return make_response(jsonify(project='succesfully added to list'), 200)
		except SanitizedException as e:
			database.session.rollback()
			print type(e), e
			return e.response(request.method)
	return make_response(jsonify(project='found'), 200)



@api.route('/list/<string:list_id>/referrals/', methods=['GET'])
@api.route('/list/<string:list_id>/referrals',  methods=['GET'])
def api_reflist_get_referrals(list_id):
	reflist = RefList.get_by_listid(list_id)
	try:
		if (not reflist): raise NoResourceFound('RefList', list_id)
		referral_ids = reflist.get_referral_ids()
		return make_response(jsonify(referrals=referral_ids), 200)
	except SanitizedException as e:
		return e.response()


#################################################################################
### TEST ROUTES #################################################################
#################################################################################


