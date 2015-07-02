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
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return e.api_response(request.method)
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
	profile = Profile.get_by_uid(session['uid'])
	ref_op	= request.values.get('operation')
	if (not reflist):	return make_response(jsonify(request='missing valid resource'),  400)
	if (not profile):	return make_response(jsonify(request='missing permission to update'), 400)
	if (not ref_op):	return make_response(jsonify(request='missing valid operation'), 400)

	# checking permissions
	if (profile.prof_id != reflist.list_profile):
		if not reflist.profile_can_modify(profile):
			return make_response(jsonify(request='missing permission to update'), 400)

	if (ref_op == 'ADD_REFERRAL'):
		referral = Referral.get_by_refid(request.values.get('referral'))
		if (not referral): return make_response(jsonify(request='missing valid referral'), 400)

		try:
			reflist.add_referral(referral)
			return make_response(jsonify(project='succesfully added to list'), 200)
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return e.api_response(request.method)
	return make_response(jsonify(project='found'), 200)


#################################################################################
### TEST ROUTES #################################################################
#################################################################################

