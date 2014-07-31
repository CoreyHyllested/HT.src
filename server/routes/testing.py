#################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
# All Rights Reserved.
#
# All information contained is the property of Insprite, LLC.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Insprite, LLC.
#################################################################################


from . import insprite_tests
from flask import render_template, make_response, session, request, redirect
from server.infrastructure.srvc_database import db_session
from server.models	import *
from server.infrastructure.errors	import *
from server.infrastructure.tasks	import *
from server.controllers				import *
from datetime import datetime as dt, timedelta
import json, smtplib, urllib




@insprite_tests.route('/send_test_emails', methods=['GET', 'POST'])
def send_all_emails():
	print 'send password recovery email'
	send_recovery_email('corey@insprite.co', 'blah blah')
	print 'send password changed email'
	send_passwd_change_email('corey@insprite.co')

	print 'send email changed email'
	send_email_change_email('corey@insprite.co', 'corey+hilarious@insprite.co')


	# Emails sends the proposal rejection email to the buyer.
	print 'send email to BUYER, rejected proposal'
	buyer_msg_html = email_body_proposal_rejected_to_buyer('url', 'the_proposal')
	buyer_msg = create_msg('TESTING-USER rejected your proposal', 'corey@insprite.co', 'COREY_TESTING', 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email('corey@insprite.co', buyer_msg)



	print 'send email to BUYER and SELLER, accepted PROPOSAL'
	buyer_name = 'corey+BUYER@insprite.co'
	buyer_addr = buyer_name
	sellr_name = 'corey+SELLER@insprite.co'
	sellr_addr = sellr_name


	sellr_html = email_body_appointment_confirmation_for_seller('TESTING-URL', buyer_name, sellr_name)
	sellr_msg = create_msg('You accepted ' + buyer_name + '\'s proposal', sellr_addr, sellr_name, 'noreply@insprite.co', u'Insprite')
	sellr_msg.attach(MIMEText(sellr_html, 'html', 'UTF-8'))
	ht_send_email(sellr_addr, sellr_msg)

	# email buyer that seller accepted their proposal.
	buyer_html = email_body_appointment_confirmation_for_buyer('TESTING-URL', buyer_name, sellr_name)
	buyer_msg = create_msg(sellr_name + ' accepted your proposal!', buyer_addr, buyer_name, 'noreply@insprite.co', u'Insprite')
	buyer_msg.attach(MIMEText(buyer_html, 'html', 'UTF-8'))
	ht_send_email(buyer_addr, buyer_msg)

	return make_response(render_template('generic_email_template.html'))


@insprite_tests.route("/disable_reviews", methods=['GET', 'POST'])
def testing_pika_celery_async():
	bp = Profile.get_by_uid(session['uid'])
	five_min = dt.utcnow() + timedelta(minutes=5);
	disable_reviews.apply_async(args=[10], eta=five_min)
	return make_response(jsonify(usrmsg="I'll try."), 200)



@insprite_tests.route("/enable_reviews", methods=['GET', 'POST'])
def testing_enable_reviews():
	bp = Profile.get_by_uid(session['uid'])
	prop_uuid = request.values.get('prop');
	proposal=Proposal.get_by_id(prop_uuid)
	enable_reviews(proposal)
	return make_response(jsonify(usrmsg="I'll try."), 200)


@insprite_tests.route("/fakereview/<buyer>/<sellr>", methods=['GET'])
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

