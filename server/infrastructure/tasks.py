from __future__ import absolute_import
from datetime import datetime as dt, timedelta
from email.mime.multipart	import MIMEMultipart
from email.mime.text		import MIMEText
from email.header			import Header
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import Appointment, Proposal, Account, Profile
from server.infrastructure.errors		 import NoProposalFound
from pprint import pprint as pp
import json, smtplib


def ht_proposal_update(p_uuid, p_from):
	# send email to buyer.   (prop_from sent you a proposal).
	# send email to seller.  (proposal has been sent)

	proposals = Proposal.query.filter_by(prop_uuid = p_uuid).all()
	if (len(proposals) != 1):
		print len(proposals)
		raise NoProposalFound(p_uuid, p_from)
	prop = proposals[0]

	(ha, hp) = get_account_and_profile(prop.prop_hero)
	(ba, bp) = get_account_and_profile(prop.prop_buyer)

	# pretty annoying.  we need to encode unicode here to utf8; decoding will fail.
	email_hero_proposal_updated(prop,  ha.email, hp.name.encode('utf8', 'ignore') , bp.name.encode('utf8', 'ignore'), bp.heroid)
	email_buyer_proposal_updated(prop, ba.email, bp.name.encode('utf8', 'ignore') , hp.name.encode('utf8', 'ignore'), hp.heroid)



def email_buyer_proposal_updated(prop, buyer_email, buyer_name, hero_name, hero_id):
	print "ebpu 1: Proposal to buyer (" + str(prop.prop_uuid) + ") last touched by", str(prop.prop_from)

	url = 'https://127.0.0.1:5000/profile?hero=' + str(hero_id)
	msg_html =	"Alright. We sent your proposal to <a href=\"" + str(url) + "\">" + hero_name + ".</a><br>"
	msg_html = msg_html + "The request was for " + str(prop.prop_ts.strftime('%A, %b %d, %Y %H:%M %p')) + " - " + str(prop.prop_tf.strftime('%A, %b %d, %Y %H:%M %p')) + "<br>"
	msg_html = msg_html + str(prop.prop_place) + "<br>" + str(prop.prop_desc) + "<br>" + str(prop.prop_cost)

	msg_subject = "Proposal sent to " + hero_name
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

	
	msg_subject = "Proposal to meet from " + buyer_name  
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
		p = Profile.query.filter_by(heroid = hero_id).all()[0]		# browsing profile
		a = Account.query.filter_by(userid = p.account).all()[0]
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
def ht_appointment_finalize(appt_id):
	print 'received appt: ', appt_id
	appointment = Appointment.query.filter_by(apptid=appt_id).all()[0]		# browsing profile
	print appointment
	print 'send final appt notice to profiles: ', appointment.buyer_prof, appointment.sellr_prof 
	(buyer_a, buyer_p) = get_account_and_profile(appointment.buyer_prof)
	(sellr_a, sellr_p) = get_account_and_profile(appointment.sellr_prof)
	print 'send final appt notice to buyer: ', buyer_a.email
	print 'send final appt notice to buyer: ', sellr_a.email

	chargeTime = appointment.ts_begin  - timedelta(days=1)
	remindTime = appointment.ts_begin  - timedelta(days=2)
	print 'charge buyer @ ' + chargeTime.strftime('%A, %b %d, %Y %H:%M %p')
	print 'remind buyer @ ' + remindTime.strftime('%A, %b %d, %Y %H:%M %p')
	send_appt_emails(sellr_a.email, buyer_a.email, appointment)
#	enque_reminder1 = ht_send_reminder_email.apply_async(args=[sellr_a.email], eta=(remindTime))
#	enque_reminder2 = ht_send_reminder_email.apply_async(args=[buyer_a.email], eta=(remindTime))
	return None

@mngr.task
def capture_creditcard():
	return None  #not defined


@mngr.task
def getTS(jsonObj):
	pp(jsonObj)
	return str(dt.now())

@mngr.task
def chargeStripe(jsonObj):
	print 'inside chargeStripe()'
	return None

@mngr.task
def enable_reviews(jsonObj):
	#is this submitted after stripe?  
	print 'enable_reviews()'
	return None

@mngr.task
def disable_reviews(jsonObj):
	#30 days after enable, shut it down!
	print 'disable_reviews()'
	return None
	

if __name__ != "__main__":
	print 'CAH: load server.tasks for @mngr.task'
else:
	print "Whoa, this is main"
