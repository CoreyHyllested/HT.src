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


from server.infrastructure.srvc_database import Base
from server.infrastructure.errors import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from datetime import datetime as dt
from pytz import timezone
import datetime
import uuid



# Appointment States
APPT_FLAG_PROPOSED = 0		# (0001) Proposed (tmp):  Shows up in dashboard as proposal.
APPT_FLAG_ACCEPTED = 1		# (0002) Accepted (tmp):  Shows up in dashboard as appointment.
APPT_FLAG_DISPUTED = 2		# (0004) disputed (tmp):  ...?
APPT_FLAG_OCCURRED = 3		# (0008) Occurred (tmp):  Shows up in dashboard as review Opp.
APPT_FLAG_REJECTED = 4		# (0010) Rejected (terminal)... see somewhere
APPT_FLAG_CANCELED = 5		# (0020) Canceled (terminal)... see somewhere
APPT_FLAG_RESOLVED = 6		# (0040) Resolved (terminal?) ...
APPT_FLAG_COMPLETE = 7		# (0080) Completed (terminal)... see somewhere

# Fake States.
APPT_FLAG_TIMEDOUT = 8		# (0100) Proposal was rejected by timeout. (Seller didn't respond).

# Occurred flags.
APPT_FLAG_BUYER_REVIEWED = 12	# (00001000)	# Appointment Reviewed:  Appointment occured.  Both reviews are in.
APPT_FLAG_SELLR_REVIEWED = 13	# (00002000)	# Appointment Reviewed:  Appointment occured.  Both reviews are in.
APPT_FLAG_MONEY_CAPTURED = 14	# (00004000)	# Appointment Captured:  Money has taken from user, 2 days after appt.
APPT_FLAG_MONEY_USERPAID = 15	# (00008000)	# Appointment Captured money and Transferred payment to Seller.
APPT_FLAG_BUYER_CANCELED = 16	# (00010000)	# Appointment was canceled by buyer.



# Appointment / Proposal Flags.  Modify aspects of meeting.
APPT_FLAG_RESPONSE	= 28	# Proposal went into negotiation.
APPT_FLAG_QUIET		= 29	# Proposal was quiet
APPT_FLAG_DIGITAL	= 30	# Proposal was digital
#APPT_FLAG_RUNOVER	= 31


APPT_STATE_PROPOSED = (0x1 << APPT_FLAG_PROPOSED)	#01		from {}  					to {accepted, rejected}		visible { dashboard-proposal }
APPT_STATE_ACCEPTED = (0x1 << APPT_FLAG_ACCEPTED)	#02		from {proposed}				to {occurred, canceled}		visible { dashboard-appointment }
APPT_STATE_DISPUTED = (0x1 << APPT_FLAG_DISPUTED)	#04		from {occurred}				to {resolved, completed}	visible { ? }
APPT_STATE_OCCURRED = (0x1 << APPT_FLAG_OCCURRED)	#08		from {accepted}				to {completed, disputed}	visible { }
APPT_STATE_REJECTED = (0x1 << APPT_FLAG_REJECTED)	#10		from {proposed}				to {}						visible {}
APPT_STATE_CANCELED = (0x1 << APPT_FLAG_CANCELED)	#20		from {accepted}				to {}						visible { history? }
APPT_STATE_RESOLVED = (0x1 << APPT_FLAG_RESOLVED)	#40		from {disputed}				to {?}						visible {}
APPT_STATE_COMPLETE = (0x1 << APPT_FLAG_COMPLETE)	#80		from {disputed, occurred}	to {}						visible {}
# Fake States.  Replaced with above.
APPT_STATE_TIMEDOUT = (0x1 << APPT_FLAG_TIMEDOUT)	#180






OAUTH_NONE   = 0
OAUTH_LINKED = 1
OAUTH_STRIPE = 2
OAUTH_GOOGLE = 3
OAUTH_FACEBK = 4
OAUTH_TWITTR = 5


REV_FLAG_CREATED = 0
REV_FLAG_FINSHED = 1
REV_FLAG_WAITING = 2
REV_FLAG_VISIBLE = 3
REV_FLAG_FLAGGED = 7
REV_FLAG_INVALID = 8

REV_STATE_CREATED = (0x1 << REV_FLAG_CREATED)
REV_STATE_FINSHED = (0x1 << REV_FLAG_FINSHED)
REV_STATE_WAITING = (0x1 << REV_FLAG_WAITING)
REV_STATE_VISIBLE = (0x1 << REV_FLAG_VISIBLE)
REV_STATE_INVALID = (0x1 << REV_FLAG_INVALID)

IMG_FLAG_PROFILE = 0	# A Profile Image
IMG_FLAG_FLAGGED = 1	# The current Profile Img, needed? -- saved in profile, right?
IMG_FLAG_VISIBLE = 2	# Image is visible or shown.  Maybe flagged, deleted, or not ready yet.
IMG_FLAG_SELLERPROF = 3	# Image is a Seller's Profile Image.

IMG_STATE_PROFILE = (0x1 << IMG_FLAG_PROFILE)
IMG_STATE_FLAGGED = (0x1 << IMG_FLAG_FLAGGED)
IMG_STATE_VISIBLE = (0x1 << IMG_FLAG_VISIBLE)
IMG_STATE_SELLERPROF = (0x1 << IMG_FLAG_VISIBLE)

MSG_FLAG_LASTMSG_READ = 0
MSG_FLAG_SEND_ARCHIVE = 1		#The original-message sender archived thread
MSG_FLAG_RECV_ARCHIVE = 2		#The original-message receiver archived thread
MSG_FLAG_THRD_UPDATED = 3		#A message was responded too.

MSG_STATE_LASTMSG_READ	= (0x1 << MSG_FLAG_LASTMSG_READ)	#1
MSG_STATE_SEND_ARCHIVE	= (0x1 << MSG_FLAG_SEND_ARCHIVE)	#2
MSG_STATE_RECV_ARCHIVE	= (0x1 << MSG_FLAG_RECV_ARCHIVE)	#4
MSG_STATE_THRD_UPDATED	= (0x1 << MSG_FLAG_THRD_UPDATED)	#8

LESSON_FLAG_STARTED = 0 		# User started to create a lesson
LESSON_FLAG_SAVED = 1 		# User completed making the lesson but saved it before finished
LESSON_FLAG_PRIVATE = 2 		# User completed making the lesson but left it private
LESSON_FLAG_ACTIVE = 3 		# User completed making the lesson and made it active

LESSON_STATE_STARTED = (0x1 << LESSON_FLAG_STARTED)	#1
LESSON_STATE_SAVED = (0x1 << LESSON_FLAG_SAVED)	#2
LESSON_STATE_PRIVATE = (0x1 << LESSON_FLAG_PRIVATE)	#4
LESSON_STATE_ACTIVE = (0x1 << LESSON_FLAG_ACTIVE)	#8

# Flags and States for Registered Users (Preview Site)

REG_FLAG_ROLE_NONE = 0
REG_FLAG_ROLE_LEARN = 1
REG_FLAG_ROLE_TEACH = 2
REG_FLAG_ROLE_BOTH = 3

REG_STATE_ROLE_NONE = (0x1 << REG_FLAG_ROLE_NONE)
REG_STATE_ROLE_LEARN = (0x1 << REG_FLAG_ROLE_LEARN)
REG_STATE_ROLE_TEACH = (0x1 << REG_FLAG_ROLE_TEACH)
REG_STATE_ROLE_BOTH = (0x1 << REG_FLAG_ROLE_BOTH)

# Profile states for teaching availability. 0 is when teaching has not been activated yet. 1 = flexible, 2 = specific

PROF_FLAG_AVAIL_NONE = 0
PROF_FLAG_AVAIL_FLEX = 1
PROF_FLAG_AVAIL_SPEC = 2

PROF_STATE_AVAIL_NONE = (0x1 << PROF_FLAG_AVAIL_NONE)
PROF_STATE_AVAIL_FLEX = (0x1 << PROF_FLAG_AVAIL_FLEX)
PROF_STATE_AVAIL_SPEC = (0x1 << PROF_FLAG_AVAIL_SPEC)

LESSON_RATE_PERHOUR = 0
LESSON_RATE_PERLESSON = 1

def set_flag(state, flag):  return (state | (0x1 << flag))
def test_flag(state, flag): return (state & (0x1 << flag))



################################################################################
#### EXAMPLE: Reading from PostgreSQL. #########################################
################################################################################
# psql "dbname=d673en78hg143l host=ec2-54-235-70-146.compute-1.amazonaws.com user=ezjlivdbtrqwgx password=lM5sTTQ8mMRM7CPM0JrSb50vDJ port=5432 sslmode=require"
# psql postgresql://name:password@instance:port/database
################################################################################


################################################################################
#### EXAMPLE: DELETING A ROW from PostgreSQL. ##################################
################################################################################
# delete from timeslot where location = 'San Francisco';
# delete from timeslot where id >= 25;
# delete from review where heroid = '559a73f1-483c-40fe-8ee5-83118ce1f7e3';

################################################################################
#### EXAMPLE: ALTER TABLE from PostgreSQL. #####################################
################################################################################
# BEGIN; 
# LOCK appointments;
# ALTER TABLE appointments ADD   COLUMN challenge   varchar(40); 
# ALTER TABLE appointments ALTER COLUMN transaction drop not null; 
# END; 
################################################################################
# BEGIN; 
# UPDATE appointment2 SET buyer_prof = 62e9e608-12cd-4b47-9eb4-ff6998dca89a WHERE 
################################################################################

################################################################################
#### EXAMPLE: INSERT ROW INTO TABLE from PostgreSQL. ###########################
################################################################################
# begin;
# insert into umsg (msg_id, msg_to, msg_from, msg_thread, msg_content, msg_created) VALUES ('testing-1-2-3-4-5', (select prof_id from profile where prof_name like '%Corey%'), (select prof_id from profile where prof_name like '%Frank%'), 'testing-1-2-3-4-5', 'Garbage in, garbage out', '2014-06-05 17:59:12.311562');
# commit;
################################################################################
 
################################################################################
#### EXAMPLE: FIND ALL DUPLICATE VALUES IN COLUMN. #############################
################################################################################
# begin;
# select count(msg_thread), msg_thread from umsg group by msg_thread having count(msg_thread) > 1;
# commit;
#### RESULTS ###################################################################
#  count |              msg_thread
# -------+--------------------------------------
#     3 | 1dfb5322-69c0-4a58-a768-ee66bcd1b9c6
#     2 | 45eb702c-1e4c-4971-94dc-44b267930854
#     5 | fd6d1310-809a-41bc-894a-da75b21aa315
################################################################################


class Account(Base):
	"""Account maintains identity information each individual."""
	__tablename__ = "account"

	USER_UNVERIFIED = 0
	USER_ACTIVE		= 1
	USER_INACTIVE	= -1
	USER_BANNED		= -2

	userid  = Column(String(40), primary_key=True, index=True, unique=True)
	email   = Column(String(128), nullable=False,  index=True, unique=True)
	name    = Column(String(128), nullable=False)
	pwhash	= Column(String(128), nullable=False)
	status  = Column(Integer,		nullable=False, default=USER_UNVERIFIED)   
	source  = Column(Integer,		nullable=False, default=OAUTH_NONE)
	phone	= Column(String(20))
	dob     = Column(DateTime())
	created = Column(DateTime())
	updated = Column(DateTime())
	sec_question = Column(String(128))
	sec_answer   = Column(String(128))
	stripe_cust	 = Column(String(64))
	role		 = Column(Integer, default = 0)

	# all user profiles
	profiles = relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

	def __init__ (self, user_name, user_email, user_pass):
		self.userid = str(uuid.uuid4())
		self.name   = user_name
		self.email  = user_email
		self.pwhash	= user_pass
		self.created = dt.utcnow()
		self.updated = dt.utcnow()

	def __repr___ (self):
		return '<Account %r, %r, %r>'% (self.userid, self.name, self.email)


	@staticmethod
	def get_by_uid(uid):
		try:
			account = Account.query.filter_by(userid=uid).one()
		except MultipleResultsFound as multiple:
			print 'Never Happen Error: caught exception looking for Account UID', uid
			account = None
		except NoResultFound as none:
			account = None
		return account

	def set_email(self, e):
		self.email = e
		self.updated = dt.utcnow()
		return self
	
	def set_name(self, n):
		self.name = n
		self.updated = dt.utcnow()
		return self
	
	def set_dob(self, bd):
		self.dob = bd
		self.updated = dt.utcnow()
		return self
		
	def set_source(self, src):
		self.source = src
		self.updated = dt.utcnow()
		return self
	
	def set_status(self, s):
		self.status = s
		self.updated = dt.utcnow()
		return self
		
	def set_sec_question(self, q):
		self.sec_question = q
		self.updated = dt.utcnow()
		return self

	def set_sec_answer(self, a):
		self.sec_answer = a
		self.updated = dt.utcnow()
		return self

	def update(self, new_values_dict):
		self.__dict__.update(new_values_dict)




class Email(Base):
	__tablename__ = "email"

	id = Column(Integer, primary_key = True)
	ht_account	= Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
	email	= Column(String(128),	nullable=False, unique=True, index=True)
	flags	= Column(Integer,		nullable=True)
	created	= Column(DateTime(),	nullable=True)
	

	def __init__ (self, account, email, flags=None):
		self.ht_account = account
		self.email = email
		self.flags = flags
		self.created = dt.utcnow()
	

	def __repr__(self):
		print '<%r>' % (self.email)


	@staticmethod
	def get_account_id(email):
		account_id = None
		try:
			user_email = Oauth.query.filter_by(email=email).one()
			account_id = user_email.ht_account
		except MultipleResultsFound as multiple:
			print 'Never Happen Error: found multiple email accounts for ', email
		except NoResultFound as none:
			print 'Error: found zero email accounts for ', email
		return account_id




class Oauth(Base):
	__tablename__ = "oauth"
	id      = Column(Integer, primary_key = True)
	ht_account	= Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)		#HT UserID
	oa_account	= Column(String(64), nullable=False, index=True)		#user id returned back		#OA UserID
	oa_service	= Column(Integer(),  nullable=False)	#LINKEDIN = 1, Google = 2					#OA Service
	oa_flags	= Column(Integer(),  nullable=False)	# (valid?									#OA Flags
	oa_email	= Column(String(128))									#OA Email
	oa_token	= Column(String(256))
	oa_secret	= Column(String(64))													#OA SECRET -- for remote call
	oa_optdata1 = Column(String(256))
	oa_optdata2 = Column(String(256))
	oa_optdata3 = Column(String(256))
	oa_created	= Column(DateTime()) 	#first login time.											#OA first
	oa_ts_login	= Column(DateTime()) 	#last  login time.


	#Oauth(uid, OAUTH_STRIPE, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
	def __init__ (self, account, service, userid, token=None, secret=None, email=None, data1=None, data2=None, data3=None):
		self.ht_account = account
		self.oa_account = userid
		self.oa_service = service
		self.oa_flags	= 0
		self.oa_created	= dt.utcnow()
		self.oa_ts_login = dt.utcnow()

		self.oa_token	= token
		self.oa_secret	= secret
		self.oa_email	= email


	def __repr__ (self):
		return '<oauth, %r %r %r>' % (self.ht_account, self.oa_service, self.oa_account)

@staticmethod
	def get_stripe_by_uid(uid):
		try:
			stripe_user = Oauth.query.filter_by(ht_account=uid).filter_by(oa_service=str(OAUTH_STRIPE)).one()
		except MultipleResultsFound as multiple:
			print 'Never Happen Error: found multiple Stripe customers for UID', uid
			stripe_user = None
		except NoResultFound as none:
			stripe_user = None
		return stripe_user


	@property
	def serialize(self):
		return {
			'ht_account'	: self.ht_account,
			'oa_account'	: self.oa_account,
			'oa_service'	: self.oa_service,
			'oa_flags'	: self.oa_flags,
			'oa_email'	: self.oa_email,
			'oa_token'	: self.oa_token,
			'oa_secret'	: self.oa_secret,
			'oa_optdata1'	: self.oa_optdata1,
			'oa_optdata2'	: self.oa_optdata2,
			'oa_optdata3'	: self.oa_optdata3,
		}




class Profile(Base):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	prof_id	= Column(String(40), primary_key=True, index=True)
	account	= Column(String(40), ForeignKey('account.userid'), nullable=False)
	prof_name	= Column(String(128), nullable=False)
	prof_vanity	= Column(String(128))
	#prof_skills	= relationship('skills', backref='profile', cascade='all,delete') 

	rating   = Column(Float(),   nullable=False, default=-1)
	reviews  = Column(Integer(), nullable=False, default=0)

	prof_img	= Column(String(128), default="no_pic_big.svg",	nullable=False) 
	prof_url	= Column(String(128), default='http://herotime.co')
	prof_bio	= Column(String(5000), default='About me')
	prof_tz		= Column(String(20))  #calendar export.
	prof_rate	= Column(Integer, nullable=False, default=40)

	industry	= Column(String(64))
	headline	= Column(String(128))
	location	= Column(String(64), nullable=False, default="Berkeley, CA")

	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")

	availability = Column(Integer, default=0)	

	#prof_img	= Column(Integer, ForeignKey('image.id'), nullable=True)  #CAH -> image backlog?
	#timeslots = relationship("Timeslot", backref='profile', cascade='all,delete', lazy=False, uselist=True, ##foreign_keys="[timeslot.profile_id]")

	def __init__ (self, name, acct):
		self.prof_id	= str(uuid.uuid4())
		self.prof_name	= name
		self.account	= acct


	def __repr__ (self):
		tmp_headline = self.headline
		if (tmp_headline is not None):
			tmp_headline = tmp_headline[:20]
		return '<profile, %r, %r, %r, %r>' % (self.prof_id, self.prof_name, self.prof_rate, tmp_headline)


	@staticmethod
	def get_by_prof_id(profile_id):
		profiles = Profile.query.filter_by(prof_id=profile_id).all()
		if len(profiles) != 1: 
			raise NoProfileFound(profile_id, 'Sorry, profile not found')
		return profiles[0]


	@staticmethod
	def get_by_uid(uid):
		profiles = Profile.query.filter_by(account=uid).all()
		if len(profiles) != 1: 
			raise NoProfileFound(uid, 'Sorry, profile not found')
		return profiles[0]


	@property
	def serialize(self):
		return {
			'account'	: str(self.account),
			'prof_id'	: str(self.prof_id),
			'prof_name'	: str(self.prof_name),
			'prof_img'	: str(self.prof_img),
			'prof_bio'	: str(self.prof_bio),
			'prof_rate'	: str(self.prof_rate),
			'headline'	: str(self.headline),
			'industry'	: str(self.industry),
		}



class Proposal(Base):
	__tablename__ = "proposal"
	prop_uuid	= Column(String(40), primary_key=True)													# NonSequential ID
	prop_hero	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE SELLER. The Hero
	prop_user	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE BUYER; requested hero.
	prop_state	= Column(Integer, nullable=False, default=APPT_STATE_PROPOSED,		index=True)			# Pure State (as in Machine)
	prop_flags	= Column(Integer, nullable=False, default=0)											# Attributes: Quiet?, Digital?, Run-Over Enabled?
	prop_count	= Column(Integer, nullable=False, default=0)											# Number of times vollied back and forth.
	prop_cost	= Column(Integer, nullable=False, default=0)											# Cost.
	prop_from	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)						# LastProfile to Touch proposal. 
	prop_ts		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	prop_tf		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	prop_tz		= Column(String(20))
	prop_desc	= Column(String(3000))
	prop_place	= Column(String(1000),	nullable = False)	
	prop_created = Column(DateTime(),	nullable = False, default = dt.utcnow())
	prop_updated = Column(DateTime(),	nullable = False, default = dt.utcnow())
	appt_secured = Column(DateTime(), nullable = True)
	appt_charged = Column(DateTime(), nullable = True)

	challengeID	= Column(String(40), nullable = False)
	charge_customer_id	= Column(String(40), nullable = True)	# stripe customer id
	charge_credit_card	= Column(String(40), nullable = True)	# stripe credit card
	charge_transaction	= Column(String(40), nullable = True)	# stripe transaction id
	charge_user_token	= Column(String(40), nullable = True)	# stripe charge tokn
	hero_deposit_acct	= Column(String(40), nullable = True)	# hero's stripe deposit account
	review_hero	= Column(String(40), ForeignKey('review.review_id'))	#TODO rename review_sellr
	review_user = Column(String(40), ForeignKey('review.review_id'))	#TODO rename review_buyer


	def __init__(self, hero, buyer, datetime_s, datetime_f, cost, location, description, token=None, customer=None, card=None, flags=None): 
		self.prop_uuid	= str(uuid.uuid4())
		self.prop_hero	= str(hero)
		self.prop_user	= str(buyer)
		self.prop_cost	= int(cost)
		self.prop_from	= str(buyer)
		if (flags is not None): self.prop_flags = flags

		self.prop_ts	= datetime_s
		self.prop_tf	= datetime_f
		self.prop_tz	= 'US/Pacific'
		self.prop_place	= location 
		self.prop_desc	= description
		self.challengeID = str(uuid.uuid4())

		self.charge_customer_id = customer
		self.charge_credit_card = card
		self.charge_user_token = token
		print 'Proposal(p_uid=%s, cost=%s, location=%s)' % (self.prop_uuid, cost, location)
		print 'Proposal(token=%s, cust=%s, card=%s)' % (token, customer, card)


	def update(self, prof_updated, updated_s=None, updated_f=None, update_cost=None, updated_place=None, updated_desc=None, updated_state=None, updated_flags=None): 
		self.prop_from = prof_updated
		self.prop_updated	= dt.utcnow()
		self.prop_count		= self.prop_count + 1

		if (updated_s is not None): self.prop_ts = updated_s
		if (updated_f is not None): self.prop_tf = updated_f
		if (updated_cost is not None):	self.prop_cost	= int(updated_cost)
		if (updated_desc is not None):	self.prop_desc	= updated_desc
		if (updated_place is not None):	self.prop_place	= updated_place
		if (updated_state is not None):	self.prop_state = updated_state
		if (updated_flags is not None):	self.prop_flags = updated_flags


	@staticmethod
	def get_by_id(prop_uuid):
		proposals = Proposal.query.filter_by(prop_uuid=prop_uuid).all()
		if len(proposals) != 1: raise NoResourceFound('Proposal', prop_uuid)
		return proposals[0]
	

	def set_flag(self, flag):
		if (flag <= APPT_FLAG_COMPLETE): raise Exception('Use set state to verify state change')
		self.prop_flags = (self.prop_flags | (0x1 << flag))


	def set_state(self, s_nxt, flag=None, uid=None, prof_id=None):
		s_cur = self.prop_state 
		flags = self.prop_flags
		valid = True
		msg = None

		if ((s_nxt == APPT_STATE_TIMEDOUT) and (s_cur == APPT_STATE_PROPOSED)):
			s_nxt = APPT_STATE_REJECTED
			flags = set_flag(flags, APPT_FLAG_TIMEDOUT)
		elif ((s_nxt == APPT_STATE_REJECTED) and (s_cur == APPT_STATE_PROPOSED)):
			if (((prof_id != self.prop_hero) and (prof_id != self.prop_user))): msg = 'REJECTOR: ' + prof_id + " isn't HERO or USER"
		elif ((s_nxt == APPT_STATE_ACCEPTED) and (s_cur == APPT_STATE_PROPOSED)):
			if (self.prop_from == uid): msg = 'LAST MODIFICATION and USER ACCEPTING PROPOSAL are same user: ' + uid
			self.appt_secured = dt.utcnow()
#		elif ((s_nxt == APPT_STATE_CAPTURED) and (s_cur == APPT_STATE_ACCEPTED)):
#			if (flag == APPT_FLAG_HEROPAID): flags = set_flag(flags, APPT_FLAG_HEROPAID)
#			flags = set_flag(flags, APPT_FLAG_USERPAID)
#			self.appt_charged = dt.now()
		elif ((s_nxt == APPT_STATE_OCCURRED) and (s_cur == APPT_STATE_ACCEPTED)):
			pass
		elif ((s_nxt == APPT_STATE_CANCELED) and (s_cur == APPT_STATE_ACCEPTED)):
			pass
		elif ((s_nxt == APPT_STATE_COMPLETE) and (s_cur == APPT_STATE_OCCURRED)):
			pass
		elif ((s_nxt == APPT_STATE_DISPUTED) and (s_cur == APPT_STATE_COMPLETE)):
			pass
		else:
			valid = False
			msg = 'Weird. The APPOINTMENT PROPOSAL is in an INVALID STATE'

		if (msg or not valid):
			raise StateTransitionError(self.prop_uuid, self.prop_state, s_nxt, flags, msg)

		self.prop_state = s_nxt
		self.prop_flags = flags
		self.prop_updated = dt.utcnow()


	def accepted(self): return (self.prop_state == APPT_STATE_ACCEPTED)
	def canceled(self): return (self.prop_state == APPT_STATE_CANCELED)
	def occurred(self): return (self.prop_state == APPT_STATE_OCCURRED)


	def get_prop_ts(self, tz=None):
		zone = self.prop_tz or 'US/Pacific'
		return self.prop_ts.astimezone(timezone(zone))


	def get_prop_tf(self, tz=None):
		zone = self.prop_tz or 'US/Pacific'
		return self.prop_tf.astimezone(timezone(zone))
			

	def __repr__(self):
		return '<prop %r, Hero=%r, Buy=%r, State=%r>' % (self.prop_uuid, self.prop_hero, self.prop_user, self.prop_state)

	@property
	def serialize(self):
		return {
			'prop_uuid'		: self.prop_uuid,
			'prop_sellr'	: self.prop_hero,
			'prop_buyer'	: self.prop_user,
			'prop_state'	: self.prop_state,
			'prop_flags'	: self.prop_flags,
			'prop_cost'		: self.prop_cost,
			'prop_updated'	: self.prop_updated.strftime('%A, %b %d, %Y %H:%M %p')
		}



class Appointment(Base):
	__tablename__ = "appointment"
	apptid		= Column(String(40), unique = True, primary_key = True, index=True)   #use challenge 
	buyer_prof	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	sellr_prof	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# if creator_id != profile_id; prop = True
	status		= Column(Integer, default=0)		#0 = free, #1 = bid on?  #2 = purchased, #4 = completed.   -1 = Removed/unlisted, #4 = canceled?

	location	= Column(String(1000), nullable = False)
	ts_begin	= Column(DateTime(),	 nullable = False)
	ts_finish 	= Column(DateTime(),	 nullable = False) # better to have this as a length of time?
	cost	= Column(Integer,	nullable = False)
	paid	= Column(Boolean,	default = False)
	cust	= Column(String(20),	nullable = False)

	description = Column(String(3000), nullable = True)
	transaction	= Column(String(40), nullable = True)	#stripe transaction 
	created		= Column(DateTime(), nullable = False)
	updated		= Column(DateTime(), nullable = False, default = datetime.datetime.now())
	agreement	= Column(DateTime(), nullable = False, default = datetime.datetime.now())

	reviewOfBuyer	= Column(String(40), ForeignKey('review.review_id'), nullable = True)
	reviewOfSellr	= Column(String(40), ForeignKey('review.review_id'), nullable = True)

	#booking_id=Column(Integer, ForeignKey('booking.id'))
	#transaction_id=Column(Integer, ForeignKey('transaction.id'))
	#transaction_id=relationship("Transaction", backref="appointment", order_by="transaction.id", lazy=False, uselist=False)
	#review_id=relationship("Review", backref="appointment", order_by="review.id", lazy=False)


	def __init__ (self):
		pass

	def __repr__ (self):
		return '<appt, b:%r, s:%r, C:%r>' % (self.buyer_prof, self.sellr_prof, self.cost)




class Image(Base):
	__tablename__ = "image"
	img_id = Column(String(64), primary_key=True)
	img_profile = Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	img_comment = Column(String(256))
	img_created = Column(DateTime())
	img_flags	= Column(Integer, default=0)
	img_order	= Column(Integer, default=0, nullable=False)
	img_lesson	= Column(String(256))

	def __init__(self, imgid, prof_id, comment=None, lesson=None):
		self.img_id  = imgid
		self.img_profile = str(prof_id)
		self.img_comment = comment
		self.img_lesson = lesson
		self.img_created = dt.utcnow()


	def __repr__ (self):
		return '<image %s %s>' % (self.img_id, self.img_comment[:20])


	@staticmethod
	def get_by_lesson_id(lesson_id):
		images = Image.query.filter_by(img_lesson=lesson_id).all()
		print 'Image.get_by_lesson_id(' + str(lesson_id) + '): ', len(images)
		return images


	@staticmethod
	def get_lesson_sample_img(lesson_id):
		sample_img = Image.query.filter_by(lesson_id=lesson_id).first()
		return sample_img


	@property
	def serialize(self):
		return {
			'img_id'		: self.img_id,
			'img_profile'	: self.img_profile,
			'img_comment'	: self.img_comment,
			'img_created'	: self.img_created,
			'img_flags'		: self.img_flags,
			'img_order'		: self.img_order,
			'img_lesson'	: self.img_lesson
		}




class LessonImageMap(Base):
	__tablename__ = "image_lesson_map"
	id			= Column(Integer, primary_key = True)
	map_image	= Column(String(64),  nullable=False, index=True)
	map_lesson	= Column(String(40),  nullable=False, index=True)
	map_prof	= Column(String(40),  nullable=True,  index=True)
	map_comm	= Column(String(256), nullable=True)
	map_order	= Column(Integer, 	  nullable=False)
	#map_flags	: use flags in Lesson and Image???
	#map_created: use timestamp in Lesson and Image???


	def __init__(self, img, lesson, profile, comment=None):
		self.map_image	= img
		self.map_lesson = lesson
		self.map_prof	= profile
		self.map_comm	= comment
		self.map_order	= -1


	def __repr__(self):
		print '<%r>' % (self.id)


	@staticmethod
	def get_images_by_lesson_id(lesson_id):
		images = Image.query.filter_by(map_lesson=lesson_id).all()
		print 'LessonImageMap.get_images_by_lesson_id(' + str(lesson_id) + '): ', len(images)
		return images




class Industry(Base):
	__tablename__ = "industry"
	industries = ['Art & Design', 'Athletics & Sports', 'Beauty & Style', 'Food', 'Music', 'Spirituality',  'Technology', 'Travel & Leisure', 'Health & Wellness', 'Other']
	enumInd = [(str(k), v) for k, v in enumerate(industries)]
	enumInd.insert(0, (-1, 'All Industries'))
	enumInd2 = [(str(k), v) for k, v in enumerate(industries)]

	id   = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False, unique=True)

	def __init__ (self, industry_name):
		self.name = industry_name

	def __repr__ (self):
		return '<industry, %r>' % (self.name)



class Skills(Base):
	__tablename__ = "skills"

	skill_id   = Column(Integer, primary_key = True)
	skill_name = Column(String(80), nullable = False)
	skill_prof = Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)

	def __init__ (self, name, prof):
		self.skill_name = name
		self.skill_prof = prof

	def __repr__ (self):
		return '<skill %r>' % (self.name)




class UserMessage(Base):
	__tablename__ = "umsg"
	msg_id		= Column(String(40), primary_key=True, unique=True)													# NonSequential ID
	msg_to		= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	msg_from	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	msg_thread	= Column(String(40), nullable=False, index=True)
	msg_parent  = Column(String(40))
	msg_content = Column(String(1024), nullable=False)
	msg_created = Column(DateTime(), nullable=False)
	msg_noticed = Column(DateTime())
	msg_opened  = Column(DateTime())
	msg_subject	= Column(String(64))
	msg_flags	= Column(Integer, default=0)


	def __init__ (self, prof_to, prof_from, content, subject=None, thread=None, parent=None):
		self.msg_id	= str(uuid.uuid4())
		self.msg_to	= str(prof_to)
		self.msg_from = str(prof_from)
		self.msg_content = str(content)
		self.msg_subject = subject
		self.msg_created = dt.utcnow()

		if (thread == None):
			# First message in thread
			thread = str(self.msg_id)
			parent = None
			if (self.msg_subject is None): raise Exception('first msg needs subject')
		else:
			# thread is not None, parent must exist; set flags properly
			if (parent == None): raise Exception('not valid threading')	
			self.msg_flags = MSG_STATE_THRD_UPDATED

		self.msg_thread	= thread
		self.msg_parent	= parent

	def __repr__(self):
		content = self.msg_content[:20]
		subject = self.msg_subject[:15]
		ts_open = self.msg_opened.strftime('%b %d %I:%M') if self.msg_opened is not None else str('Unopened')
		return '<umsg %r|%r\t%r\t%r\t%r\t%r\t%r>' % (self.msg_id, self.msg_thread, self.msg_parent, self.msg_flags, ts_open, self.msg_from, subject)


	@staticmethod
	def get_by_msg_id(uid):
		msgs = UserMessage.query.filter_by(msg_id=uid).all()
		if len(msgs) != 1: raise NoResourceFound('UserMessage', uid)
		return msgs[0]


	@property
	def serialize(self):
		return {
			'msg_id'		: str(self.msg_id),
			'msg_to'		: self.msg_to,
			'msg_from'		: self.msg_from,
			'msg_flags'		: self.msg_flags,
			'msg_subject'	: str(self.msg_subject),
			'msg_content'	: str(self.msg_content),
			'msg_parent'	: str(self.msg_parent),
			'msg_thread'	: str(self.msg_thread),
		}


	def archived(self, profile_id):
		if (profile_id == self.msg_to):		return (self.msg_flags & MSG_STATE_RECV_ARCHIVE)
		if (profile_id == self.msg_from):	return (self.msg_flags & MSG_STATE_SEND_ARCHIVE)
		raise Exception('profile_id(%s) does not match msg(%s) TO or FROM' % (profile_id, self.msg_id))
		




class Review(Base):
	__tablename__ = "review"

	enumRating = [(str(k), v) for k, v in enumerate(['Overall Value', 'Poor Value','Fair Value','Good Value','Great Value','Excellent Value'])]
	review_id		= Column(String(40), primary_key=True, index=True)
	prof_reviewed	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	prof_authored	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)

	rev_status	= Column(Integer, default=REV_STATE_CREATED, index=True)	#TODO rename state
	rev_appt	= Column(String(40), nullable = False)	# should be appt.
	rev_twin    = Column(String(40), unique = True) 	#twin or sibling review

	appt_score = Column(Integer, nullable = False, default = -1)	# 1 - 5
	appt_value = Column(Integer, nullable = False, default = -1)	# in dollars.

	score_attr_time = Column(Integer)	#their time management skills
	score_attr_comm = Column(Integer)	#their communication skills
	generalcomments = Column(String(5000))

	#rev_created = Column(DateTime(), nullable = False) # needed?
	rev_updated	= Column(DateTime(), nullable = False)
	rev_flags   = Column(Integer, default=0)	 #TODO what is this for?  Needed? 


	def __init__ (self, prop_id, prof_reviewed, prof_author):
		self.review_id = str(uuid.uuid4())
		self.rev_appt = prop_id 
		self.prof_reviewed = prof_reviewed
		self.prof_authored = prof_author
		self.rev_updated = dt.utcnow()


	def __repr__ (self):
		tmp_comments = self.generalcomments

		if (tmp_comments is not None):
			tmp_comments = tmp_comments[:20]
		return '<review %r; by %r, %r, %r>' % (self.prof_reviewed, self.prof_authored, self.appt_score, tmp_comments)



	@staticmethod
	def get_by_id(rev_id):
		try:
			review = Review.query.filter_by(review_id=rev_id).one()
		except MultipleResultsFound as mrf:
			print 'Never Happen Error: caught exception looking for Account UID', rev_id
			review = None
		except NoResultsFound as nrf:
			review = None
		return review



	def consume_review(self, appt_score, appt_value, appt_comments, attr_time=None, attr_comm=None):
		self.appt_score = appt_score
		self.appt_value = appt_value
		self.generalcomments = appt_comments



	def validate_author(self, session_prof_id):
		if (self.prof_authored != session_prof_id):
			raise ReviewError('validate', self.prof_authored, session_prof_id, 'Something is wrong, try again')
			return "no fucking way -- review author matches current profile_id"
		print 'we\'re the intended audience'


	def time_until_review_disabled(self):
		# (utcnow - updated) is a timedelta object.
		#print 'Right now the time is\t' + str(dt.utcnow().strftime('%A, %b %d %H:%M %p'))
		#print 'The review updated_ts\t' + str(review.rev_updated.strftime('%A, %b %d %H:%M %p'))
		return (dt.utcnow() - self.rev_updated).days

		
	def completed(self):
		mask = REV_STATE_FINSHED | REV_STATE_VISIBLE
		return (self.rev_status & mask)


	def set_state(self, s_nxt, flag=None, prof_id=None):
		s_cur = self.rev_status
		flags = self.rev_flags
		valid = True
		msg = None

		if ((s_nxt == REV_STATE_FINSHED) and (s_cur == REV_STATE_CREATED)):
			if (self.time_until_review_disabled() < 0):
				msg = 'Reviews may only be submitted 30 days after a meeting'
				valid = False
		elif ((s_nxt == REV_STATE_FINSHED) and (s_cur == REV_STATE_FINSHED)):
			msg	= 'Reviews cannot be modified once submitted'
			valid = False
		elif ((s_nxt == REV_STATE_VISIBLE) and (s_cur == REV_STATE_FINSHED)):
			pass
		elif ((s_nxt == REV_STATE_VISIBLE) and (s_cur == REV_STATE_VISIBLE)):
			# used for testing.
			pass
		elif ((s_nxt == REV_STATE_INVALID) and (s_cur == REV_STATE_CREATED)):
			pass
		else:
			valid = False
			msg = 'Weird. The Review is in an INVALID STATE'

		if (not valid):
			raise StateTransitionError(self.review_id, self.rev_status, s_nxt, msg=msg)

		self.rev_status = s_nxt
		self.rev_updated = dt.utcnow()


	def get_review_url(self):
		return '/review/new/' + str(self.review_id)




class Lesson(Base):
	__tablename__ = "lesson"

	LESSON_LOC_ANY = 0
	LESSON_LOC_BUYER = 1
	LESSON_LOC_SELLER = 2

	LESSON_AVAIL_DEFAULT = 0
	LESSON_AVAIL_SPECIFIC = 1


	# Lesson Description
	lesson_id			= Column(String(40), primary_key=True, index=True)
	lesson_profile		= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	lesson_title		= Column(String(128))
	lesson_description	= Column(String(5000))
	lesson_industry		= Column(String(64))

	# Lesson Availability
	lesson_avail		= Column(Integer, default=LESSON_AVAIL_DEFAULT)
	lesson_duration		= Column(Integer)

	# Lesson Location
	lesson_loc_option	= Column(Integer, default=LESSON_LOC_ANY)
	lesson_address_1	= Column(String(64))
	lesson_address_2	= Column(String(64))
	lesson_city			= Column(String(64))
	lesson_state		= Column(String(10))
	lesson_zip			= Column(String(10))
	lesson_country		= Column(String(64))
	lesson_address_details = Column(String(256))

	# Lesson Metadata
	lesson_updated	= Column(DateTime())
	lesson_created	= Column(DateTime(), nullable=False)
	lesson_flags	= Column(Integer, default=0)

	# Lesson Cost
	lesson_rate = Column(Integer)
	lesson_rate_unit = Column(Integer, default=LESSON_RATE_PERHOUR)


	def __init__ (self, profile_id):
		self.lesson_id	= str(uuid.uuid4())
		self.lesson_profile	= profile_id
		self.lesson_created = dt.utcnow()


	def __repr__ (self):
		return '<Lesson: %r, %r, %r>' % (self.lesson_id, self.lesson_profile, self.lesson_title)


	@staticmethod
	def get_by_lesson_id(lesson_id):
		lessons = Lesson.query.filter_by(lesson_id=lesson_id).all()
		if len(lessons) != 1: 
			raise NoLessonFound(lesson_id, 'Sorry, lesson not found')
		return lessons[0]




class Registrant(Base):
	"""Account for interested parties signing up through the preview.insprite.co."""
	__tablename__ = "registrant"

	reg_userid  = Column(String(40), primary_key=True, index=True, unique=True)
	reg_email   = Column(String(128), index=True, unique=True)
	reg_location = Column(String(128))
	reg_ip = Column(String(20))
	reg_name    = Column(String(128))
	reg_org    = Column(String(128))	
	reg_referrer = Column(String(128))
	reg_flags = Column(Integer, default=0)
	reg_created = Column(DateTime())
	reg_updated = Column(DateTime())
	reg_comment = Column(String(1024))


	def __init__ (self, reg_email, reg_location, reg_ip, reg_org, reg_referrer, reg_flags, reg_comment):
		self.reg_userid = str(uuid.uuid4())
		self.reg_email  = reg_email
		self.reg_location  = reg_location
		self.reg_ip  = reg_ip
		self.reg_org  = reg_org
		self.reg_referrer  = reg_referrer
		self.reg_flags  = reg_flags
		self.reg_comment = reg_comment
		self.reg_created = dt.utcnow()
		self.reg_updated = dt.utcnow()


	def __repr___ (self):
		return '<Registrant %r, %r, %r, %r>'% (self.reg_userid, self.reg_email, self.reg_location, self.reg_flags)


	@staticmethod
	def get_by_regid(regid):
		registrants = Registrant.query.filter_by(reg_userid=regid).all()
		if len(registrants) != 1: raise NoAccountFound(regid, 'Sorry, no account found')
		return registrants[0]


