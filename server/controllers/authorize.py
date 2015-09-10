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


import smtplib, urlparse
import oauth2 as oauth
import uuid

from pprint	import pprint as pp
from datetime import datetime as dt
from flask.sessions		import SessionInterface, SessionMixin
from werkzeug.security	import generate_password_hash
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server import sc_server
from server.infrastructure import errors
from server.models import *
from server.controllers.annotations import *
from server.controllers.database	import *
from server.controllers.email		import *
from server.controllers.forms		import *



def bind_session(account, profile):
	""" preserve userid server-side """
	#http://stackoverflow.com/questions/817882/unique-session-id-in-python
	session['pid']	= profile.prof_id
	session['uid']	= account.userid
	session['role'] = account.role
	trace('bound session sid[' + str(session.get_sid()) + '] uid[' + str(session['uid']) + '] ' + str(session['role']))



def sc_authenticate_user_with_oa(oa_srvc, oa_data_raw):
	""" Returns authenticated account. Iff account doesn't exist -- create it. """

	print 'normalize oauth account data', oa_srvc
	oa_data = normalize_oa_account_data(oa_srvc, oa_data_raw)

	hero = None
	oauth_account = []

	try:
		print 'search Oauth for', oa_srvc, oa_data['oa_account']
		oauth_accounts = sc_server.database.session.query(Oauth)																		\
								   .filter((Oauth.oa_service == oa_srvc) & (Oauth.oa_account == oa_data['oa_account']))	\
								   .all()
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()

	if len(oauth_accounts) == 1:
		print 'found oauth account for individual'
		oa_account = oauth_accounts[0]
		hero = Account.get_by_uid(oa_account.ht_account)
	else:
		print 'found ', len(oauth_accounts), 'so sign up user with this oauth account.'
		(hero, prof) = sc_create_account_with_oauth(oa_data['oa_name'], oa_data['oa_email'], oa_srvc, oa_data)
		#import_profile(prof, oa_srvc, oa_data)
	return hero



def sc_password_recovery(email):
	""" Password recovery """
	account = Account.get_by_email(email)
	if (account is None): raise NoAccountFound(email)

	newquestion = account.reset_security_question()
	if (not newquestion):
		raise AccountError(email, 'Security challenge not created.')
	sc_send_password_recovery_link(account)




# orig from sc_create_account
#	gift_id = session.pop('gift_id', None)
#	if (gift_id):
#		try:
#			# claim gift
#			gift = GiftCertificate.get_by_giftid(gift_id)
#			gift.gift_state = CertificateState.CLAIMED
#			gift.gift_recipient_name = profile.prof_name
#			gift.gift_recipient_prof = profile.prof_id
#			gift.gift_dt_updated = dt.utcnow();
#			sc_server.database.session.add(gift)
#			sc_server.database.session.commit()
#		except Exception as e:
#			print type(e), e
#			sc_server.database.session.rollback()





def sc_create_account_with_oauth(name, email, oa_provider, oa_data):
	print 'sc_create_account_with_oauth: ', name, email, oa_provider
	try:
		profile = sc_create_account(name, email, str(uuid.uuid4()))
	except AccountError as ae:
		print ae

	if (profile is None):
		print 'create_account failed. happens when same email address is used'
		print 'Right, now mention an account uses this email address.'
		print 'Eventually.. save oa variables; put session variable.  Redirect them to login again.  If they can.  Merge account.'
		return None, None

	try:
		print 'create oauth account'
		#get account from profile.... 
		oa_user = Oauth(str(account.userid), oa_provider, oa_data['oa_account'], token=oa_data['oa_token'], secret=oa_data['oa_secret'], email=oa_data['oa_email'])
		sc_server.database.session.add(oa_user)
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print type(ie), ie
		sc_server.database.session.rollback()
		return None, None 
	except Exception as e:
		print type(e), e
		sc_server.database.session.rollback()
		return None, None
	return (account , profile)




def import_profile(bp, oauth_provider, oauth_data):
	oa_data = normalize_oa_profile_data(oauth_provider, oauth_data)
	try:
		linked_id = oauth_data.get('id')
		summary   = oauth_data.get('summary')
		#recommend = oauth_data.get('recommendationsReceived')
		headline  = oauth_data.get('headline')
		industry  = oauth_data.get('industry')
		location  = oauth_data.get('location')

		print ("update profile")
		if (summary  is not None): bp.prof_bio = summary
		if (headline is not None): bp.headline = headline
		if (industry is not None): bp.industry = industry #linked_in_sanatize(INDUSTRY, industry)
		if (location['name'] is not None): bp.location = location['name'] #linked_in_sanatize(LOCATION, loc[name])

		print 'hero & prof created', bp.account, oauth_provider 
		oauth = Oauth(str(bp.account), oauth_provider, linked_id, token=session.get('linkedin_token'))

		sc_server.database.session.add(bp)
		sc_server.database.session.add(oauth)
		print ("committ update bp")
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print 'ah fuck, it failed', ie
		sc_server.database.session.rollback()
	except Exception as e:
		print 'ah fuck, it failed other place', e
		sc_server.database.session.rollback()




def normalize_oa_profile_data(provider, oa_data):
	data = {}
	if provider == OauthProvider.LINKED:
		data['summary']	= oa_data.get('summary', None)
		data['headline'] = oa_data.get('headline', None)
		data['industry'] = oa_data.get('industry', None)
		data['location'] = oa_data.get('location', None)
		#recommend = oauth_data.get('recommendationsReceived')
	return data


def normalize_oa_account_data(provider, oa_data):
	data = {}
	print 'normalizing oauth data'
	if provider == OauthProvider.LINKED:
		data['oa_service']	= provider
		data['oa_account']	= oa_data.get('id')
		data['oa_email']	= oa_data.get('CAH_email', None)
		data['oa_token']	= oa_data.get('CAH_token', None)
		data['oa_secret']	= oa_data.get('CAH_sec', None)
	elif provider == OauthProvider.FACEBK:
		facebook = oa_data

		print 'normalize facebook data'
		data['oa_service']	= provider
		data['oa_account']	= facebook['id']
		data['oa_name']		= facebook['name']
		data['oa_email']	= facebook['email']
		data['oa_token']	= facebook['token']
		data['oa_secret']	= None
		data['oa_timezone'] = facebook.get('timezone', None)
		pp(data)

	return data

