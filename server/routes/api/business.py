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


import re
from server import sc_server
from server.models import *
from server.routes import api_routing as api
from server.routes import test_routes as test
from server.routes.helpers import *
from server.controllers import *




@api.route('/business/create', methods=['GET'])
def render_business_create():
	resp_code	= 200
	resp_mesg	= 'Done'
	trustent	= NewTrustedEntityForm(request.values)
	fragment	= render_template('/fragments/business-create.html', form=trustent)
	return make_response(jsonify(sc_msg=resp_mesg, embed=fragment), resp_code)



@api.route('/business/create/', methods=['POST'])
@api.route('/business/create',  methods=['POST'])
def api_business_create_post():
	form = NewTrustedEntityForm(request.form)
	if form.validate_on_submit():
		print 'name', form.name.data, form.site.data, form.email.data, form.phone.data
		business = Business(form.name.data, phone=form.phone.data, email=form.email.data, website=form.site.data)
		business.bus_state = BusinessSource.set(business.bus_state, BusinessSource.USER_ADDED)

		try:
			database.session.add(business)
			database.session.commit()
			print 'committed', business
		except Exception as e:
			database.session.rollback()
			print type(e), e
			return make_response(jsonify(error=str(e)), 500)

		return make_response(jsonify(success=True, business=business.serialize), 200)
	elif request.method == 'POST':
		print 'render_b_create: invalid ' + str(form.errors)
	return make_response(jsonify(functionality='Undefined'), 400)



@sc_server.csrf.exempt
@api.route('/business/<string:bus_id>/', methods=['GET'])
@api.route('/business/<string:bus_id>',  methods=['GET'])
def api_business_read(bus_id):
	business = Business.get_by_id(bus_id, check_json=True)
	if (business): return make_response(jsonify(business.serialize_id), 200)
	return make_response(jsonify(id='Business,' + bus_id + ', not found'), 400)



@sc_server.csrf.exempt
@api.route('/business/<string:pro_id>/update/', methods=['POST'])
@api.route('/business/<string:pro_id>/update',  methods=['POST'])
def api_business_update(pro_id):
	print 'api_business_update(): enter'
	return make_response(jsonify(functionality='Undefined'), 400)


@api.route('/business/<string:pro_id>/destroy/', methods=['DELETE'])
@api.route('/business/<string:pro_id>/destroy',	 methods=['DELETE'])
def api_business_destroy(pro_id):
	return make_response(jsonify(functionality='Undefined'), 400)




@api.route('/business/search/<string:identifier>/', methods=['GET','POST'])
@api.route('/business/search/<string:identifier>',  methods=['GET','POST'])
def api_business_search(identifier):
	business_idx = Business.get_json_index()

	identifier = identifier.strip().lower()
	identphone = re.sub('[() \-,.]', '', identifier)

	fromdb = Business.search(identifier)
	response = {}

	for hit in fromdb:
		# check to see if any locations match; update address
		response[hit.bus_id] = { "id": hit.bus_id, "name": hit.bus_name, "addr" : 'No address listed', "combined" : hit.bus_name }
		print response[hit.bus_id]

	for pro in business_idx.values():
		if (len(response) > 5): break

		if identifier in pro.get('business_name','').lower():
			print 'adding', pro['business_name'], 'because we matched', pro['business_name'].lower(), 'to', identifier
			address = 'No address listed'
			if (pro['address']):
				street	= pro['address'].get('street')
				suite	= pro['address'].get('suite')
				city	= pro['address'].get('city')
				state	= pro['address'].get('state')

				if (street and suite):
					address = street + ', ' + suite + ' '
				elif (street):
					address = street + ' '

				if (city and state):
					address = address + city + ', ' + state
				elif (city):
					address = address + city
			combined = pro['business_name'] + ' | ' + address
			response[pro['_id']] = { "id": pro["_id"], "name" : pro['business_name'], "addr" : address, "combined" : combined }

		phone = pro.get('phone', '')
		if phone: phone = re.sub('[() \-,.]', '', phone)
		if phone and (identphone in phone):
			print 'added', pro['name'], 'because we matched', pro['phone'], 'to', identphone
			#response[pro['_id']] = { "id": pro["_id"], "name" : pro['name'], "addr" : pro['addr'].get('street', 'No address listed') }
	return make_response(jsonify(response), 200)





def api_business_info_by_phone(identifier):
	business_idx = Business.get_json_index()
	print 'api_business(%s)' % (identifier)

