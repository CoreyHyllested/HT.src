from server.infrastructure.srvc_database import Base
from server.infrastructure.errors import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt
import datetime
import uuid


APPT_FLAG_PROPOSED = 0
APPT_FLAG_RESPONSE = 1
APPT_FLAG_ACCEPTED = 2
APPT_FLAG_CAPTURED = 3
APPT_FLAG_OCCURRED = 4
APPT_FLAG_REVIEWED = 5
APPT_FLAG_COMPLETE = 6
APPT_FLAG_DISPUTED = 7
APPT_FLAG_RESOLVED = 8

APPT_FLAG_USERPAID = 15		# if buyer has paid us.
APPT_FLAG_HEROPAID = 16		# if hero has been paid.
APPT_FLAG_TIMEDOUT = 17		# why proposal was rejected
APPT_FLAG_CANCELED = 18		# use from to see who canceled it

APPT_FLAG_QUIET		= 29
APPT_FLAG_DIGITAL	= 30
APPT_FLAG_RUNOVER	= 31


APPT_STATE_PROPOSED = (0x1 << APPT_FLAG_PROPOSED)	#1
APPT_STATE_RESPONSE = (0x1 << APPT_FLAG_RESPONSE)	#2
APPT_STATE_ACCEPTED = (0x1 << APPT_FLAG_ACCEPTED)	#4
APPT_STATE_CAPTURED = (0x1 << APPT_FLAG_CAPTURED)	#8
APPT_STATE_OCCURRED = (0x1 << APPT_FLAG_OCCURRED)	#16
APPT_STATE_REVIEWED = (0x1 << APPT_FLAG_REVIEWED)
APPT_STATE_COMPLETE = (0x1 << APPT_FLAG_COMPLETE)
APPT_STATE_DISPUTED = (0x1 << APPT_FLAG_DISPUTED)
APPT_STATE_TIMEDOUT = (0x1 << APPT_FLAG_TIMEDOUT)

APPT_STATE_REJECTED = -1
APPT_STATE_CANCELED = -3






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

 


class Account(Base):
	"""Account maintains identity information each individual."""
	__tablename__ = "account"

	USER_UNVERIFIED = 0
	USER_ACTIVE		= 1
	USER_INACTIVE	= -1
	USER_BANNED		= -2

	userid  = Column(String(40), primary_key=True, index=True, unique=True)
	email   = Column(String(120), nullable=False,  index=True, unique=True)
	name    = Column(String(120), nullable=False)
	pwhash	= Column(String(120), nullable=False)
	status  = Column(Integer,		nullable=False, default=USER_UNVERIFIED)   
	source  = Column(Integer,		nullable=False, default=OAUTH_NONE)
	phone	= Column(String(20))
	dob     = Column(DateTime())
	created = Column(DateTime())
	updated = Column(DateTime())
	sec_question = Column(String(120))
	sec_answer   = Column(String(50))

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



class Oauth(Base):
	__tablename__ = "oauth"
	id      = Column(Integer, primary_key = True)
	account = Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
	oa_service	= Column(String(40), nullable=False)	#LINKEDIN = 1, Google = 2
	oa_userid	= Column(String(40), nullable=False, index=True)	#user id returned back
	opt_token	= Column(String(200))
	opt_email	= Column(String(120))
										#linkedin	#Stripe		#Google
	opt_data1	= Column(String(200))	#?			CC token
	opt_data2	= Column(String(200))	#?			Dflt CC		
	opt_data3	= Column(String(200))	#?			chrge key	

	#Oauth(uid, OAUTH_STRIPE, stripe_cust_userid, data1=cc_token, data2=stripe_card_dflt)
	def __init__ (self, account, provider, userid, token=None, data1=None, data2=None, data3=None):
		self.account = account		# account.userid
		self.oa_service	= provider
		self.oa_userid	= userid		# third_party user_ID 
		self.opt_token	= token		# opt_token for accessing accounts
		self.opt_email	= None
		self.opt_data1	= data1		# opt_value
		self.opt_data2	= data2		# opt_value
		self.opt_data3	= data3		

	def __repr__ (self):
		return '<oauth, %r %r %r>' % (self.account, self.oa_service, self.oa_userid)
		
	@staticmethod
	def get_stripe_by_uid(uid):
		stripe_custs = Oauth.query.filter_by(account=uid).filter_by(oa_service=str(OAUTH_STRIPE)).all()
		if (len(stripe_custs) != 1): raise NoOauthFound(uid, OAUTH_STRIPE)
		return stripe_custs[0]



class Profile(Base):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	prof_id	= Column(String(40), primary_key=True, index=True)
	account	= Column(String(40), ForeignKey('account.userid'), nullable=False)
	prof_name	= Column(String(120),							nullable=False)
	prof_vanity	= Column(String(100))
	#prof_skills	= relationship('skills', backref='profile', cascade='all,delete') 

	rating   = Column(Float(),   nullable=False, default=-1)
	reviews  = Column(Integer(), nullable=False, default=0)

	prof_img	= Column(String(120), default="no_pic_big.svg",	nullable=False) 
	prof_url	= Column(String(120), default='http://herotime.co')
	prof_bio	= Column(String(5000), default='About me')
	prof_tz		= Column(String(20))  #calendar export.
	prof_rate	= Column(Integer, nullable=False, default=40)

	industry	= Column(String(50))
	headline	= Column(String(50))
	location	= Column(String(50), nullable=False, default="Berkeley, CA")

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
		print "len = ", len(profiles), profile_id
		if len(profiles) != 1: 
			raise NoProfileFound(profile_id, 'Sorry, profile not found')
		return profiles[0]

	@staticmethod
	def get_by_uid(uid):
		profiles = Profile.query.filter_by(account=uid).all()
		print "len = ", len(profiles), uid
		if len(profiles) != 1: 
			raise NoProfileFound(uid, 'Sorry, profile not found')
		return profiles[0]


		

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
	def get_by_id(prop_id, location=None):
		proposals = Proposal.query.filter_by(prop_uuid=prop_id).all()
		if len(proposals) != 1: raise NoResourceFound('Proposal', prop_id)
		return proposals[0]
	


	def set_state(self, s_nxt, flag=None, uid=None, prof_id=None):
		s_cur = self.prop_state 
		flags = self.prop_flags
		valid = True
		msg = None


		if ((s_nxt == APPT_STATE_RESPONSE) and ((s_cur == APPT_STATE_PROPOSED) or (s_cur == APPT_STATE_RESPONSE))):
			self.prop_count = self.prop_count + 1
		elif ((s_nxt == APPT_STATE_TIMEDOUT) and ((s_cur == APPT_STATE_PROPOSED) or (s_cur == APPT_STATE_RESPONSE))):
			s_nxt = APPT_STATE_REJECTED
			flags = set_flag(flags, APPT_FLAG_COMPLETE)
			flags = set_flag(flags, APPT_FLAG_TIMEDOUT)
		elif ((s_nxt == APPT_STATE_REJECTED) and ((s_cur == APPT_STATE_PROPOSED) or (s_cur == APPT_STATE_RESPONSE))):
			if (((prof_id != self.prop_hero) and (prof_id != self.prop_user))): msg = 'REJECTOR: ' + prof_id + " isn't HERO or USER"
			flags = set_flag(flags, APPT_FLAG_COMPLETE)
		elif ((s_nxt == APPT_STATE_ACCEPTED) and ((s_cur == APPT_STATE_PROPOSED) or (s_cur == APPT_STATE_RESPONSE))):
			if (self.prop_from == uid): msg = 'LAST MODIFICATION and USER ACCEPTING PROPOSAL are same user: ' + uid
			self.appt_secured = dt.utcnow()
		elif ((s_nxt == APPT_STATE_CAPTURED) and (s_cur == APPT_STATE_ACCEPTED)):
			if (flag == APPT_FLAG_HEROPAID): flags = set_flag(flags, APPT_FLAG_HEROPAID)
			flags = set_flag(flags, APPT_FLAG_USERPAID)
			self.appt_charged = dt.now()
		elif ((s_nxt == APPT_STATE_OCCURRED) and (s_cur == APPT_STATE_CAPTURED)):
			pass
		elif ((s_nxt == APPT_STATE_REVIEWED) and (s_cur == APPT_STATE_OCCURRED)):
			pass
		elif ((s_nxt == APPT_STATE_CANCELED) and ((s_cur == APPT_STATE_ACCEPTED) or (s_cur == APPT_STATE_CAPTURED))):
			flags = set_flag(flags, APPT_FLAG_COMPLETE)
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
	#img_x, int
	#img_y, int

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


	def __init__ (self, prof_to, prof_from, content, thread=None, thread_parent=None):
		print 'running usrmessage init'
		self.msg_id	= str(uuid.uuid4())
		self.msg_to	= str(prof_to)
		self.msg_from = str(prof_from)
		self.msg_content = str(content)
		self.msg_created = dt.utcnow()

		if (thread == None):
			thread = str(self.msg_id)
			thread_parent = None
		else:
			raise Exception('no threading exists')
			# if not thread_parent suggested, raise an error

		self.msg_thread	= thread
		self.msg_parent	= thread_parent

	def __repr__(self):
		content = self.msg_content[:20]
		return '<umsg: %r %r<=>%r [%r]>' % (self.msg_id, self.msg_to, self.msg_from, content) 




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

