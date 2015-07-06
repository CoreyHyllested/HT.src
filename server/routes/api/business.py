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


import os, re
from server import sc_server
from server.models import *
from server.routes import api_routing as api
from server.routes import test_routes as test
from server.routes.helpers import *
from server.controllers import *



@api.route('/business/<string:bus_id>/', methods=['GET'])
@api.route('/business/<string:bus_id>',  methods=['GET'])
def api_business_read(bus_id):
	print 'api_business(%s)' % (bus_id)

	business_idx = get_business_index()
	business = business_idx.get(bus_id, { "id" : "Not Found"})
	return make_response(jsonify(business), 200)



@sc_server.csrf.exempt
@api.route('/business/create', methods=['POST'])
def api_business_create():
	print 'api_business_create(): enter'
	return make_response(jsonify(functionality='Undefined'), 400)



@sc_server.csrf.exempt
@api.route('/business/<string:pro_id>/update/', methods=['POST'])
@api.route('/business/<string:pro_id>/update',	methods=['POST'])
def api_business_update(pro_id):
	print 'api_business_update(): enter'
	return make_response(jsonify(functionality='Undefined'), 400)




@api.route('/business/search/<string:identifier>/', methods=['GET','POST'])
@api.route('/business/search/<string:identifier>',  methods=['GET','POST'])
def api_business_search(identifier):
	business_idx = get_business_index()

	identifier = identifier.rstrip('.json').strip().lower()
	identphone = re.sub('[() \-,.]', '', identifier)

	response = {}
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


			response[pro['_id_factual']] = { "id": pro["_id_factual"], "name" : pro['business_name'], "addr" : address }

	#	email = pro.get('email', '')
	#	if email and (identifier in pro['email'].lower()):
	#		print 'adding', pro['name'], 'because we matched', pro['email'].lower(), 'to', identifier 
			#response[pro['id_factual']] = { "id": pro["id_factual"], "name" : pro['name'], "addr" : pro['addr'].get('street', 'No address listed') }
	#		continue
		phone = pro.get('phone', '')
		if phone: phone = re.sub('[() \-,.]', '', phone)
		if phone and (identphone in phone):
			print 'added', pro['name'], 'because we matched', pro['phone'], 'to', identphone
			response[pro['id_factual']] = { "id": pro["id_factual"], "name" : pro['name'], "addr" : pro['addr'].get('street', 'No address listed') }
	pp (response)
	return make_response(jsonify(response), 200)




def get_business_index():
	if (sc_server.__dict__.get('pro_index_id')):
		# return the professional business index.
		return sc_server.__dict__['pro_index_id']

	try:
		print 'Priming Search.'
		fp = open(os.getcwd() + '/server/static/root/companies.json')
		sc_server.pro_list = json.loads(fp.read())
		sc_server.pro_index_id = {}
		for account in sc_server.pro_list:
			sc_server.pro_index_id[account['_id_factual']] = account
	except Exception as e:
		print type(e), e
	finally:
		if (fp): fp.close()

	print len(sc_server.pro_list), type(sc_server.pro_list)
	return sc_server.pro_index_id




def api_business_info_by_phone(identifier):
	business_idx = get_business_index()
	print 'api_business(%s)' % (identifier)
