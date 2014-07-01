from server.infrastructure.srvc_database import Base
from server.infrastructure.errors import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt
import datetime
import uuid



# Appointment States
APPT_FLAG_PROPOSED = 0		# Proposed (tmp):  Shows up in dashboard as proposal.
APPT_FLAG_ACCEPTED = 1		# Accepted (tmp):  Shows up in dashboard as appointment.
APPT_FLAG_DISPUTED = 2		# disputed (tmp):  ...?
APPT_FLAG_OCCURRED = 3		# Occurred (tmp):  Shows up in dashboard as review Opp.
PROP_FLAG_REJECTED = 4		# Rejected (terminal)... see somewhere
APPT_FLAG_CANCELED = 5		# Canceled (terminal)... see somewhere
APPT_FLAG_RESOLVED = 6		# Resolved (terminal?) ...
APPT_FLAG_COMPLETE = 7		# Completed (terminal)... see somewhere

# Fake States.
APPT_FLAG_TIMEDOUT = 8		# Proposal was rejected by timeout. (Seller didn't respond).

# Occurred flags.
APPT_FLAG_BUYER_REVIEWED = 12		# Appointment Reviewed:  Appointment occured.  Both reviews are in.
APPT_FLAG_SELLR_REVIEWED = 13		# Appointment Reviewed:  Appointment occured.  Both reviews are in.
APPT_FLAG_MONEY_CAPTURED = 14		# Appointment Captured:  Money has taken from user, 2 days after appt.
APPT_FLAG_MONEY_USERPAID = 15		# Appointment Captured money and Transferred payment to Seller.
APPT_FLAG_BUYER_CANCELED = 16		# Appointment was canceled by buyer.



# Appointment / Proposal Flags.  Modify aspects of meeting.
APPT_FLAG_RESPONSE	= 28	# Proposal went into negotiation.
APPT_FLAG_QUIET		= 29	# Proposal was quiet
APPT_FLAG_DIGITAL	= 30	# Proposal was digital
#APPT_FLAG_RUNOVER	= 31


APPT_STATE_PROPOSED = (0x1 << APPT_FLAG_PROPOSED)	#01
APPT_STATE_ACCEPTED = (0x1 << APPT_FLAG_ACCEPTED)	#02
APPT_STATE_DISPUTED = (0x1 << APPT_FLAG_DISPUTED)	#04
APPT_STATE_OCCURRED = (0x1 << APPT_FLAG_OCCURRED)	#08
APPT_STATE_REJECTED = (0x1 << APPT_FLAG_REJECTED)	#10
APPT_STATE_CANCELED = (0x1 << APPT_FLAG_CANCELED)	#20
APPT_STATE_RESOLVED = (0x1 << APPT_FLAG_RESOLVED)	#40
APPT_STATE_COMPLETE = (0x1 << APPT_FLAG_COMPLETE)	#80
# Fake States.  Replaced with above.
APPT_STATE_TIMEDOUT = (0x1 << APPT_FLAG_TIMEDOUT)	#180






OAUTH_NONE   = 0
OAUTH_LINKED = 1
OAUTH_STRIPE = 2
OAUTH_GOOGLE = 3
OAUTH_FACEBK = 4
OAUTH_TWITTR = 5


REV_FLAG_CREATED = 0
REV_FLAG_ENABLED = 1
REV_FLAG_WAITING = 2
REV_FLAG_VISIBLE = 3
REV_FLAG_FLAGGED = 7
REV_FLAG_NOTUSED = 8

REV_STATE_CREATED = (0x1 << REV_FLAG_CREATED)
REV_STATE_ENABLED = (0x1 << REV_FLAG_ENABLED)
REV_STATE_WAITING = (0x1 << REV_FLAG_WAITING)
REV_STATE_VISIBLE = (0x1 << REV_FLAG_VISIBLE)
REV_STATE_NOTUSED = (0x1 << REV_FLAG_NOTUSED)

IMG_FLAG_PROFILE = 0	# A Profile Image
IMG_FLAG_FLAGGED = 1	# The current Profile Img, needed? -- saved in profile, right?
IMG_FLAG_VISIBLE = 2	# Image is visible or shown.  Maybe flagged, deleted, or not ready yet.

IMG_STATE_PROFILE = (0x1 << IMG_FLAG_PROFILE)
IMG_STATE_FLAGGED = (0x1 << IMG_FLAG_FLAGGED)
IMG_STATE_VISIBLE = (0x1 << IMG_FLAG_VISIBLE)


MSG_FLAG_LASTMSG_READ = 0
MSG_FLAG_SEND_ARCHIVE = 1		#The original-message sender archived thread
MSG_FLAG_RECV_ARCHIVE = 2		#The original-message receiver archived thread
MSG_FLAG_THRD_UPDATED = 3		#A message was responded too.

MSG_STATE_LASTMSG_READ	= (0x1 << MSG_FLAG_LASTMSG_READ)	#1
MSG_STATE_SEND_ARCHIVE	= (0x1 << MSG_FLAG_SEND_ARCHIVE)	#2
MSG_STATE_RECV_ARCHIVE	= (0x1 << MSG_FLAG_RECV_ARCHIVE)	#4
MSG_STATE_THRD_UPDATED	= (0x1 << MSG_FLAG_THRD_UPDATED)	#8

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

#	@staticmethod
#	def get_by_prof_id(profile_id):
#		accounts = Account.query.filter_by(profiles.prof_id=profile_id).all()
#		if len(accounts) != 1: raise NoAccountFound(uid, 'Sorry, no account found')
#		return accounts[0]

	@staticmethod
	def get_by_uid(uid):
		accounts = Account.query.filter_by(userid=uid).all()
		if len(accounts) != 1: raise NoAccountFound(uid, 'Sorry, no account found')
		return accounts[0]

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


#class Email(Base):
#	__tablename__ = "email"

#	id = Column(Integer, primary_key = True)
#	ht_account	= Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
#	email	= Column(String(128),	nullable=False)
#	flags	= Column(Integer,		nullable=False)
	
#	def __init__ (self, account, email, flags=None):
#		self.ht_account = account
#		self.email = email

	


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
		stripe_custs = Oauth.query.filter_by(ht_account=uid).filter_by(oa_service=str(OAUTH_STRIPE)).all()
		if (len(stripe_custs) != 1): raise NoOauthFound(uid, OAUTH_STRIPE)
		return stripe_custs[0]


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

	updated = Column(DateTime(), nullable=False, default = dt.utcnow())
	created = Column(DateTime(), nullable=False, default = dt.utcnow())

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
	prop_ts		= Column(DateTime(timezone=True),   nullable = False)
	prop_tf		= Column(DateTime(timezone=True),   nullable = False)
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
	review_hero	= Column(String(40), ForeignKey('review.review_id'))
	review_user = Column(String(40), ForeignKey('review.review_id'))

	#Proposal(hp.prof_id, bp.prof_id, dt_start, dt_finsh, (prop_cost), location=prop_place, description=prop_desc, token=stripe_tokn, cust=pi, card=stripe_card)
	def __init__(self, hero, buyer, datetime_s, datetime_f, cost, location, description, token=None, customer=None, card=None, flags=None): 
		self.prop_uuid	= str(uuid.uuid4())
		self.prop_hero	= str(hero)
		self.prop_user	= str(buyer)
		self.prop_cost	= int(cost)
		self.prop_from	= str(buyer)
		if (flags is not None): self.prop_flags = flags

		self.prop_ts	= datetime_s
		self.prop_tf	= datetime_f
		self.prop_place	= location 
		self.prop_desc	= description
		self.challengeID = str(uuid.uuid4())

		self.charge_customer_id = customer
		self.charge_credit_card = card
		self.charge_user_token = token


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
		return (self.flags | (0x1 << flag))


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
#		elif ((s_nxt == APPT_STATE_OCCURRED) and (s_cur == APPT_STATE_CAPTURED)):
#			pass
		elif ((s_nxt == APPT_STATE_REVIEWED) and (s_cur == APPT_STATE_OCCURRED)):
			pass
		elif ((s_nxt == APPT_STATE_CANCELED) and (s_cur == APPT_STATE_ACCEPTED)):
			#TODO disable / do not fire reviews.
		elif ((s_nxt == APPT_STATE_COMPLETE) and ((s_cur == APPT_STATE_REVIEWED) or (s_cur == APPT_STATE_OCCURRED))):
			flags = set_flag(flags, APPT_FLAG_COMPLETE)
		elif ((s_nxt == APPT_STATE_DISPUTED) and ((s_cur == APPT_STATE_REVIEWED) or (s_cur == APPT_STATE_COMPLETE))):
			flags = set_flag(flags, APPT_FLAG_DISPUTED)
			flags = set_flag(flags, APPT_FLAG_COMPLETE)
		else:
			valid = False
			msg = 'Weird. The APPOINTMENT PROPOSAL is in an INVALID STATE'

		if (msg or not valid):
			raise StateTransitionError(self.prop_uuid, self.prop_state, s_nxt, flags, msg)

		self.prop_state = s_nxt
		self.prop_flags = flags
		self.prop_updated = dt.utcnow()
			

	def __repr__(self):
		return '<prop %r, Hero=%r, Buy=%r, State=%r>' % (self.prop_uuid, self.prop_hero, self.prop_user, self.prop_state)




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

	def __init__(self, imgid, prof_id, comment=None):
		self.img_id  = imgid
		self.img_profile = str(prof_id)
		self.img_comment = comment
		self.img_created = dt.utcnow()

	def __repr__ (self):
		return '<image %s %s>' % (self.img_id, self.img_profile)



class Industry(Base):
	__tablename__ = "industry"
	industries = ['Art & Design', 'Athletics & Sports', 'Beauty & Style', 'Food', 'Music', 'Spirituality',  'Technology', 'Travel & Leisure', 'Health & Wellness', 'Other']
	enumInd = [(str(k), v) for k, v in enumerate(industries)]

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

	rev_status	= Column(Integer, default=REV_STATE_CREATED, index=True)
	rev_appt	= Column(String(40), nullable = False)	# should be appt.
	rev_twin    = Column(String(40), unique = True) 	#twin or sibling review

	appt_score = Column(Integer, nullable = False, default = -1)	# 1 - 5
	appt_value = Column(Integer, nullable = False, default = -1)	# in dollars.

	score_attr_time = Column(Integer)	#their time management skills
	score_attr_comm = Column(Integer)	#their communication skills
	generalcomments = Column(String(5000))

	#rev_created = Column(DateTime(), nullable = False, default = dt.utcnow()) # needed?
	rev_updated	= Column(DateTime(), nullable = False, default = dt.utcnow())
	rev_flags   = Column(Integer, default=0)	 #TODO what is this for?  Needed? 

	def __init__ (self, prop_id, usr_reviewed, usr_author):
		self.review_id = str(uuid.uuid4())
		self.rev_appt = prop_id 
		self.prof_reviewed = usr_reviewed
		self.prof_authored = usr_author

	def __repr__ (self):
		tmp_comments = self.generalcomments

		if (tmp_comments is not None):
			tmp_comments = tmp_comments[:20]
			
		return '<review %r; by %r, %r, %r>' % (self.prof_reviewed, self.prof_authored, self.appt_score, tmp_comments)


	def consume_review(self, appt_score, appt_value, appt_comments, attr_time=None, attr_comm=None):
		self.appt_score = appt_score
		self.appt_value = appt_value
		self.generalcomments = appt_comments


	@staticmethod
	def retreive_by_id(find_id):
		reviews = Review.query.filter_by(review_id=find_id).all()
		if len(reviews) != 1: raise NoReviewFound(find_id, 'Sorry, review not found')
		return reviews


	def validate (self, session_prof_id):
		if (self.prof_authored != session_prof_id):
			raise ReviewError('validate', self.prof_authored, session_prof_id, 'Something is wrong, try again')
			return "no fucking way -- review author matches current profile_id"

		
	def if_posted(self, flag):
		return (self.rev_status & (0x1 << flag))

