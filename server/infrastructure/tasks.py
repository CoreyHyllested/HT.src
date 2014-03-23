from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from email.header			import Header
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from pprint import pprint as pp
import json, smtplib
import stripe


def ht_proposal_update(p_uuid, p_from):
	# send email to buyer.   (prop_from sent you a proposal).
	# send email to seller.  (proposal has been sent)

	proposals = Proposal.query.filter_by(prop_uuid = p_uuid).all()
	if (len(proposals) != 1): raise NoProposalFound(p_uuid, p_from)
	prop = proposals[0]

	(ha, hp) = get_account_and_profile(prop.prop_hero)
	(ba, bp) = get_account_and_profile(prop.prop_user)

	# pretty annoying.  we need to encode unicode here to utf8; decoding will fail.
	email_hero_proposal_updated(prop,  ha.email, hp.prof_name.encode('utf8', 'ignore') , bp.prof_name.encode('utf8', 'ignore'), bp.prof_id)
	email_buyer_proposal_updated(prop, ba.email, bp.prof_name.encode('utf8', 'ignore') , hp.prof_name.encode('utf8', 'ignore'), hp.prof_id)



def email_buyer_proposal_updated(prop, buyer_email, buyer_name, hero_name, hero_id):
	url = 'https://127.0.0.1:5000/profile?hero=' + str(hero_id)
	msg_html =	"Alright. We sent your proposal to <a href=\"" + str(url) + "\">" + hero_name + ".</a><br>"
	msg_html = msg_html + "The request was for " + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal to meet " + hero_name
	if (prop.prop_count > 1): msg_subject = msg_subject + "(updated)"

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(msg_subject, 'utf-8')
	msg['To']	= "\"%s\" <%s>" % (Header(buyer_name, 'utf-8'), buyer_email)
	msg['From'] = "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	msg.attach(MIMEText(msg_html, 'html', 'UTF-8'))
	ht_send_email(buyer_email, msg) 


def email_hero_proposal_updated(prop, hero_email, hero_name, buyer_name, buyer_id):
	print "Proposal to hero (" + str(prop.prop_uuid) + ") last touched by", str(prop.prop_from)

	url = 'https://127.0.0.1:5000/profile?hero=' + str(buyer_id)
	msg_html =	"Congrats. <br>";
	msg_html = msg_html + "<a href=\"" + url + "\">" 
	msg_html = msg_html + buyer_name 
	msg_html = msg_html + " </a> wants to buy your time.<br>"
	msg_html = msg_html + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	
	msg_subject = "Proposal to meet " + buyer_name  
	if (prop.prop_count > 1): msg_subject = msg_subject + " (updated)"

	msg = MIMEMultipart('alternative')
	msg['Subject']	= '%s'  % Header(msg_subject, 'utf-8')
	msg['To']		= "\"%s\" <%s>" % (Header(hero_name, 'utf-8'), hero_email)
	msg['From']		= "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(hero_email, msg) 


@mngr.task
def send_recovery_email(toEmail, challenge_hash):
	url = 'https://herotime.co/newpassword/' + str(challenge_hash) + "?email=" + str(toEmail)
	
	#prop_state	= Column(Integer, nullable=False, default=APPT_PROPOSED, index=True)
	#prop_created = Column(DateTime(), nullable = False)

	



def get_account_and_profile(hero_id):
	try:
		p = Profile.query.filter_by(prof_id = hero_id).all()[0]		# browsing profile
		a = Account.query.filter_by(userid  = p.account).all()[0]
	except Exception as e:
		print "Oh shit, caught error at get_account_and_profile" + e
		raise e
	return (a, p)


@mngr.task
def getDBCorey(x):
	print ('in getDBCorey' + str(x))
	accounts = Account.query.filter_by(email=('corey.hyllested@gmail.com')).all()
	print ('accounts = ' + str(len(accounts)))
	if (len(accounts) == 1):
		print str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)
	print 'exit getDBCorey'
	return str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)



@mngr.task
def send_verification_email(toEmail, uid, challenge_hash):
	url  = 'https://herotime.co/signup/verify/' + str(challenge_hash) + "?email="+str(toEmail)+"&uid=" + str(uid)
	msg_text = "Thank you for creating a HeroTime account. Click <a href=\"" + str(url) + "\">here</a> to verify your email."
	msg_html = "Thank you for creating a HeroTime account. Go to " + str(url) + " to verify your email."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password Verification"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg) 


@mngr.task
def send_recovery_email(toEmail, challenge_hash):
	url = 'https://herotime.co/newpassword/' + str(challenge_hash) + "?email=" + str(toEmail)
	msg_text = "Go to " + url + " to recover your HeroTime password."
	msg_html = "Click <a href=\"" + url + "\">here</a> to recover your HeroTime password."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password Recovery"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)


@mngr.task
def send_welcome_email(email_addr):
	msg_text = "Welcome to HeroTime!\nNow go buy and sell time. Enjoy.\n"
	msg_html = """\n<html><head></head><body>Welcome to HeroTime!<br><br>Now go buy and sell time. Enjoy.</body></html>"""

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Welcome to HeroTime"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = email_addr 
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_text, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(email_addr, msg)


@mngr.task
def send_email_change_email(toEmail, newEmail):
	msg_html = "Your HeroTime email has been changed to " + newEmail + ". If you did not make this change please let us know."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Email address changed"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html'))
	ht_send_email(toEmail, msg)


@mngr.task
def send_passwd_change_email(toEmail):
	msg_html = "Your HeroTime password has been updated."

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Password changed"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = toEmail
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	msg.attach(MIMEText(msg_html, 'html' ))
	ht_send_email(toEmail, msg)



@mngr.task
def send_proposal_reject_emails(hero_email_addr, hero_name, buyer_email_addr, buyer_name, prop):
	hero_msg_html = "Hey, hero you can put away your cape and cowl for now..  You rejected proposal %s from USER." % (prop)
	hero_msg = MIMEMultipart('alternative')
	hero_msg['Subject']	= '%s'  % Header('HeroTime rejection notice.', 'utf-8')
	hero_msg['To']	 = "\"%s\" <%s>" % (Header(hero_name, 'utf-8'), hero_email_addr)
	hero_msg['From'] = "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_email_addr, hero_msg)

	buyer_msg_html = "Hey, keep your money.  Your hero is in another castle.  Your hero rejected your proposal %s." % (prop)
	buyer_msg = MIMEMultipart('alternative')
	buyer_msg['Subject']	= '%s'  % Header('HeroTime rejection notice.', 'utf-8')
	buyer_msg['To']			= "\"%s\" <%s>" % (Header(buyer_name, 'utf-8'), buyer_email_addr)
	buyer_msg['From']		= "\"%s\" <%s>" % (Header(u'HeroTime', 'utf-8'), 'noreply@herotime.co')
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)


@mngr.task
def send_appt_emails(hero_email_addr, buyer_email_addr, appt):
	print 'sending appt emails@ ' + appt.ts_begin.strftime('%A, %b %d, %Y -- %H:%M %p')
	hero_msg_html = "Hey, Hero.  You have your cape and cowl.  You have an appointment on %s. was accepted." % (appt)
	hero_msg = MIMEMultipart('alternative')
	hero_msg['Subject'] = "HeroTime Appointment Confirmation."
	hero_msg['From'] = "noreply@herotime.co"
	hero_msg['To'] = hero_email_addr   #can be email name?
	hero_msg['fromname'] = "HeroTime"
	hero_msg.attach(MIMEText(hero_msg_html, 'plain'))
	ht_send_email(hero_email_addr, hero_msg)

	buyer_msg_html = "Congrats.  You have an appointment setup on %s. was accepted." % (appt)
	buyer_msg = MIMEMultipart('alternative')
	buyer_msg['Subject'] = "HeroTime Appointment Confirmation."
	buyer_msg['From'] = "noreply@herotime.co"
	buyer_msg['To'] = buyer_email_addr   #can be email name?
	buyer_msg['fromname'] = "HeroTime"
	buyer_msg.attach(MIMEText(buyer_msg_html, 'plain'))
	ht_send_email(buyer_email_addr, buyer_msg)



@mngr.task
def send_prop_rejected_email(email_addr, proposal):
	msg_html = "Your HeroTime Proposal, %s, was rejected." % (proposal)

	msg = MIMEMultipart('alternative')
	msg['Subject'] = "HeroTime Proposal Rejected"
	msg['From'] = "noreply@herotime.co"
	msg['To'] = email_addr   #can be email name?
	msg['fromname'] = "HeroTime"
	msg.attach(MIMEText(msg_html, 'plain'))
	ht_send_email(email_addr, msg)


@mngr.task
def ht_send_email(toEmail, msg):
	# SendGrid login; TODO, move into config file.
	username = 'radnovic'
	password = "HeroTime"

	# Open a connection to the SendGrid mail server
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s = smtplib.SMTP('smtp.sendgrid.net', 587)
	s.login(username, password)
	s.sendmail('noreply@herotime.co', toEmail, msg.as_string())
	s.quit()





@mngr.task
def ht_appointment_finalize(appt_id,  stripe_cust, stripe_card, stripe_tokn):
	print 'ht_appointment_finailze() appt: ', appt_id, ", cust: ", stripe_cust, ", card: ", stripe_card, ", token: ", stripe_tokn 
	appointment = Appointment.query.filter_by(apptid=appt_id).all()[0]		# browsing profile
	print appointment
	print 'send final appt notice to profiles: ', appointment.buyer_prof, appointment.sellr_prof 
	(ba, bp) = get_account_and_profile(appointment.buyer_prof)
	(ha, hp) = get_account_and_profile(appointment.sellr_prof)
	print 'send final appt notice to buyer: ', ba.email
	print 'send final appt notice to sellr: ', ha.email

	chargeTime = appointment.ts_begin  - timedelta(days=1)
	remindTime = appointment.ts_begin  - timedelta(days=2)
	print 'charge buyer @ ' + chargeTime.strftime('%A, %b %d, %Y %H:%M %p')
	print 'remind buyer @ ' + remindTime.strftime('%A, %b %d, %Y %H:%M %p')
	send_appt_emails(ha.email, ba.email, appointment)
	
	(ha, hp) = get_account_and_profile(appointment.sellr_prof)
	(ba, bp) = get_account_and_profile(appointment.buyer_prof)
	# add timestamp to ensure it hasn't been tampered with; also send cost; 
	print 'calling ht_capturecard -- delayed'
	rc = ht_capture_creditcard(appointment.apptid, ba.email, bp.prof_name.encode('utf8', 'ignore'), stripe_card, stripe_cust) #, eta=chargeTime):
	print 'back from ht_capturecard -- delayed, ', rc



	print 'returning from ht_appt_finalize'
#	enque_reminder1 = ht_send_reminder_email.apply_async(args=[sellr_a.email], eta=(remindTime))
#	enque_reminder2 = ht_send_reminder_email.apply_async(args=[buyer_a.email], eta=(remindTime))
	return None


@mngr.task
def ht_proposal_reject(p_uuid, rejector):
	print 'received proposal uuid: ', p_uuid 

	proposals = Proposal.query.filter_by(prop_uuid = p_uuid).all()
	if len(proposals) == 0: raise NoProposalFound(p_uuid, rejector)
	the_proposal = proposals[0]
	the_propsoal.status = APPT_REJECTED

	# get data to send emails
	(ha, hp) = get_account_and_profile(the_proposal.prop_hero)
	(ba, bp) = get_account_and_profile(the_proposal.prop_user)
#	print 'will send prop reject notice to buyer: ', ba.email, ba.userid, bp.prof_name.encode('utf8', 'ignore')
#	print 'will send prop reject notice to sellr: ', ha.email, ha.userid, hp.prof_name.encode('utf8', 'ignore')

	# bit of over-engineering; 
	if (rejector != ha.userid and rejector != ba.userid):	#only Hero / Buyer can reject proposal
		raise PermissionDenied('reject prop', rejector, 'You do not have permission to reject this proposal')

	try: # delete proposal 
		db_session.delete(the_proposal)
		db_session.commit()
	except Exception as e:
		# cleanup DB immediately
		db_session.rollback()
		print 'DB error:', e
		raise DB_Error(e, 'Shit that\'s embarrassing')

	print 'send rejection emails to profiles: ', the_proposal.prop_hero, the_proposal.prop_user
	send_proposal_reject_emails(ha.email, hp.prof_name.encode('utf8', 'ignore'), ba.email, bp.prof_name.encode('utf8', 'ignore'), the_proposal)





@mngr.task
def getTS(jsonObj):
	pp(jsonObj)
	return str(dt.now())

@mngr.task
def enable_reviews(the_appointment):
	#is this submitted after stripe?  
	hp = the_appointment.sellr_prof
	bp = the_appointment.buyer_prof

	print 'enable_reviews()'

	review_hp = Review(hp, bp, None, None)
	review_bp = Review(bp, hp, None, None)
	
	the_appointment.status = APPT_CAPTURED
	the_appointment.reviewOfBuyer = review_bp.id
	the_appointment.reviewOfSellr = review_hp.id

	try:
		db_session.add(the_appointment)
		db_session.add(review_hp)
		db_session.add(review_bp)
		db_session.commit()
		# TODO create two events to send in 1 hr after meeting completion to do review
	except Exception as e:
		db_session.rollback()
		print e	
	
	return None

@mngr.task
def disable_reviews(jsonObj):
	#30 days after enable, shut it down!
	print 'disable_reviews()'
	return None


@mngr.task
def ht_capture_creditcard(appt_id, buyer_email, buyer_name, buyer_cc_token, buyer_cust_token):
	#CAH TODO may want to add the Oauth_id to search and verify the cust_token isn't different
	print 'ht_capture_creditecard called: buyer_cust_token = ', buyer_cust_token, ", buyer_cc_token=", buyer_cc_token
	the_appointment = Appointment.query.filter_by(apptid=appt_id).all()[0]		# browsing profile
	print the_appointment

	if (the_appointment.status == APPT_CANCELED):
		print 'state is cancled'

#	print str(the_appointment.updated)
#	print str(appointment.ts_begin)
#	print str(appointment.ts_finish)
	print str(the_appointment.cust)

	try:
		charge = stripe.Charge.create (
			customer=buyer_cust_token, 	#		customer.id is the second one passed in
			#stripe_cust = Oauth(uid, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
			amount=(the_appointment.cost * 100),
			currency='usd',
			description=the_appointment.description,
			#application_fee=int((the_appointment.cost * 7.1)-30),
			api_key="sk_test_nUrDwRPeXMJH6nEUA9NYdEJX"
					#if this key is an api_key -- i.e. someone's customer key -- e.g. the heros' customer key
			#-- subtracted stripe's fee?  -(30 +(ts.cost * 2.9)  
		)

	except Exception as e:
		#Cannot apply an application_fee when the key given is not a Stripe Connect OAuth key.
		print e
	print 'That\'s all folks, it should have worked?'


	pp(charge)
	print 'Post Charge'
	print charge['customer']

#	Transaction 
	#transaction.timestamp = dt.utcnow()
	#transaction.timestamp = charge['id']  #charge ID
	#transaction.timestamp = charge['amount']  # same amount?
	#transaction.timestamp = charge['captured']  #True, right?
	#transaction.timestamp = charge['paid']  # == true, right?
	#transaction.timestamp = charge['livemode']  # == true, right?
	#transaction.timestamp = charge['balance_transaction']
	#transaction.timestamp = charge['card']['id']
	#transaction.timestamp = charge['card']['customer']
	#transaction.timestamp = charge['card']['fingerprint']


	#print charge['balance_transaction']
	print charge['failure_code']
	#print charge['failure_message']

	#queue two events to create review.  Need to create two addresses.
	print 'calling enable_reviews'
	enable_reviews(the_appointment)
	print 'returning out of charge'
	



def get_stripe_customer(uid=None, cc_token=None, cc_card=None):
	stripe.api_key = "sk_test_nUrDwRPeXMJH6nEUA9NYdEJX"
	stripe_cust = None
	#check db for stripe.

	print 'check db oauth stripe account'

	stripe_custs = Oauth.query.filter_by(account=uid).all()
	if (len(stripe_custs) == 1):
		print 'get stripe customer from DB' 

		# we could update the card with cc_card right here.
		#stripe api to get jsob obj from stripe; 

		print 'return get_stripe_cust (', stripe_custs[0].opt_token, ')'
		return stripe_custs[0].opt_token


	print 'create customer from stripe API' 
	try:
		print 'create Customer w/ cc = ' + str(cc_token)
		stripe_cust_json	= stripe.Customer.create(card=cc_token, description=str(uid))
		stripe_cust_userid	= stripe_cust_json['id']
		stripe_card_dflt	= stripe_cust_json['default_card']
		print stripe_cust_json

		stripe_cust = Oauth(uid, OAUTH_STRIPE, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
		print stripe_cust
		db_session.add(stripe_cust)
		db_session.commit()
		print 'and ... saved to db'
	except UnboundLocalError as ule:
		print str(e)
		# raise ThisWasAlreadySubmitted (check back with RC. 
		# will need to grab asynch_submit RC -- stuff it in the appointment.
	except Exception as e:
		#problems with customer create
		print str(e)
		db_session.rollback()

	print 'return get_stripe_cust (', stripe_cust_userid, ')'
	return stripe_cust_userid
	#should have both credit card token, customer token, 


	

if __name__ != "__main__":
	print 'CAH: load server.tasks for @mngr.task'
else:
	print "Whoa, this is main"
