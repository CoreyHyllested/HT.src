from server.infrastructure.srvc_database import Base
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
import datetime, uuid


TS_PROP_BY_HERO = 0
TS_PROP_BY_USER = 1
TS_USER_ACCEPTD = 2
TS_PROP_PURCHSD = 2
TS_PROP_COMPLTD = 4

TS_HERO_REMOVED = -1
TS_APP_CANCELED = -2

#APPT_DISPUTED		= -2
#APPT_CANCELED		= -1 
APPT_HAVE_AGREEMENT	=  0
APPT_CARD_CAPTURED	=  1   #money is captured, heros will get paid
APPT_SEND_REVIEWS	=  2   #24 hours after meeting, send reviews
APPT_POST_REVIEWS	=  3   #30 days after meeting, post reviews

    #x) current status (state machine? :: proposed, prop_in_negotiation, prop_rejected; appt; appt_canceled; appt_completed. 

APPT_PROPOSED = 0
APPT_RESPONSE = 1
APPT_ACCEPTED = 2
APPT_CAPTURED = 4
APPT_OCCURRED = 8
APPT_REVIEWED = 16

#APPT_REVIEWED = 32
#APPT_REVIEWED = 64
#APPT_REVIEWED = 128
#APPT_REVIEWED = 256
APPT_REVIEWED = 512

APPT_REJECTED = 1024
APPT_CANCELED = 2048
APPT_DISPUTED = 4096

APPT_FLAGS_NONE	= 0

################################################################################
#### EXAMPLE: Reading from PostgreSQL. #########################################
################################################################################
# psql "dbname=d673en78hg143l host=ec2-54-235-70-146.compute-1.amazonaws.com user=ezjlivdbtrqwgx password=lM5sTTQ8mMRM7CPM0JrSb50vDJ port=5432 sslmode=require"
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
# ALTER TABLE timeslot 	   ADD   COLUMN challenge   varchar(40); 
# ALTER TABLE appointments ALTER COLUMN transaction drop not null; 
# END; 
################################################################################
# BEGIN; 
# UPDATE appointment2 SET buyer_prof = 62e9e608-12cd-4b47-9eb4-ff6998dca89a WHERE 
 


class Account(Base):
	"""Account maintains identity information each individual."""
	__tablename__ = "account"
	USER_UNVERIFIED = 0
	USER_ACTIVE		= 1
	USER_INACTIVE	= -1
	USER_BANNED		= -2

	userid  = Column(String(40), primary_key=True,            unique=True)
	email   = Column(String(120), nullable=False, index=True, unique=True)
	name    = Column(String(120), nullable=False)
	pwhash	= Column(String(120), nullable=False)
	status  = Column(Integer,		nullable=False, default=USER_UNVERIFIED)   
	source  = Column(Integer,		nullable=False, default=0)   # 0 = User created id here. Else: Linkedin = 1, FB = 2, Google = 3, Twitter = 4, StackOverflow = 5
	dob     = Column(DateTime())
	created = Column(DateTime())
	sec_question = Column(String(120))
	sec_answer   = Column(String(50))
	# optional phone number?
	# add stripe ID
	# add stripe token?

	# all user profiles
	profiles = relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

	def __init__ (self, user_name, user_email, user_pass):
		self.userid = str(uuid.uuid4())
		self.name   = user_name
		self.email  = user_email
		self.pwhash	= user_pass
		self.created = datetime.datetime.now()

	def __repr___ (self):
		return '<Account %r, %r, %r>'% (self.userid, self.name, self.email)

	def set_email(self, e):
		self.email = e
		return self
	
	def set_name(self, n):
		self.name = n
		return self
	
	def set_dob(self, bd):
		self.dob = bd
		return self
		
	def set_source(self, src):
		self.source = src
		return self
	
	def set_status(self, s):
		self.status = s
		return self
		
	def set_sec_question(self, q):
		self.sec_question = q
		return self

	def set_sec_answer(self, a):
		self.sec_answer = a
		return self

	def update(self, new_values_dict):
		self.__dict__.update(new_values_dict)



#class Oauth(Base):
#	__tablename__ = "oauth_accounts"
#	id      = Column(Integer, primary_key = True)
#	account = Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
#	oa_name = Column(String(40),									nullable=False)
#	oa_user = Column(String(40),									nullable=False)
#	token   = Column(String(120),									nullable=False)



class OauthStripe(Base):
	""" Account for maintaining stripe info """ 

	__tablename__ = "oauth_stripe"
	id      = Column(Integer, primary_key = True)
	account = Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
	stripe  = Column(String(40), nullable=False, index=True)
	token   = Column(String(40), nullable=False)
	pubkey  = Column(String(40), nullable=False)

	def __init__ (self, account):
		self.account = account

	def __repr__ (self):
		return '<oauth_stripe, %r %r %r>' % (self.account, self.stripe, self.token)
		



class Profile(Base):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	id       = Column(Integer, primary_key=True)	
	heroid   = Column(String(40), index=True, unique=True, nullable=False)
	account  = Column(String(40), ForeignKey('account.userid'), nullable=False)
	name     = Column(String(120), 								 nullable=False)
	imgURL	 = Column(String(120), default="no_pic_big.svg",		 nullable=False) 
	skills	 = Column(String(120), 								 nullable=True) #CSV => #x, #y, #z
	vanity   = Column(String(100), 								 nullable=True)

	rating   = Column(Float(),   nullable=False, default=-1)
	reviews  = Column(Integer(), nullable=False, default=0)

	img      = Column(Integer, ForeignKey('image.id'), nullable=True)  #CAH -> image backlog?
	url      = Column(String(120),  default='http://herotime.co')
	bio      = Column(String(5000), default='About me')

	industry   = Column(String(50), nullable=True)
	headline   = Column(String(50), nullable=True)
	location   = Column(String(50), nullable=False, default="Berkeley, CA")
	baserate   = Column(Integer,    nullable=False, default=100)
	negotiable = Column(Boolean,	  nullable=False, default=True)

#    timeslots = relationship("Timeslot", backref='profile', cascade='all,delete', uselist=True, lazy=False)
	#timeslots = relationship("Timeslot", backref='profile', cascade='all,delete', lazy=False, uselist=True, ##foreign_keys="[timeslot.profile_id]")
	
	zipcode  = Column(Integer)
	timezone = Column(String(20))  #calendar export.
	updated = Column(DateTime(), nullable=False, default = datetime.datetime.now())
	created = Column(DateTime(), nullable=False, default = datetime.datetime.now())

	def __init__ (self, profile_name, acct):
		self.name = profile_name
		self.heroid  = str(uuid.uuid4())
		self.account = acct

	def __repr__ (self):
		return '<profile, %r, %r, %r, %r>' % (self.heroid, self.name, self.baserate, self.headline[:20])
		

	# x) UUID
    # x) Seller/ Hero
    # x) Buyer
    # x) meeting start time (datetime, timezone)
    # x) meeting length of time
    # x) can run over?
    # x) cost
    # x) Location
    # x) description
    # x) init create time
    # x) updated time
    # x) negotiation_count (iterations)
    # x) negotiator_to_respond.

    #x) current status (state machine? :: proposed, prop_in_negotiation, prop_rejected; appt; appt_canceled; appt_completed. 
    # 14) Buyer's Stripe Cust hash
    # 15) Buyer's Stripe Card hash


class Proposal(Base):
	__tablename__ = "proposal"
	id			= Column(Integer, primary_key = True)
	prop_uuid	= Column(String(40), nullable = False)													# NonSequential ID
	prop_hero	= Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)			# THE SELLER. The Hero
	prop_buyer	= Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)			# THE BUYER; requested hero.
	prop_state	= Column(Integer, nullable=False, default=APPT_PROPOSED, index=True)
	prop_flags	= Column(Integer, nullable=False, default=APPT_FLAGS_NONE)								# Quiet?, Digital?, Run-Over Enabled?
	prop_count	= Column(Integer, nullable=False, default=0)
	prop_cost	= Column(Integer, nullable=False, default=0)
	prop_from	= Column(String(40), ForeignKey('profile.heroid'), nullable=False)						# LastProfile to Touch proposal. 
	prop_ts		= Column(DateTime(),   nullable = False)
	prop_tf		= Column(DateTime(),   nullable = False)
	prop_place	= Column(String(1000), nullable = False)
	prop_desc	= Column(String(3000), nullable = True)
	prop_created = Column(DateTime(), nullable = False)
	stripe_cust	= Column(String(40), nullable = True)
	stripe_card	= Column(String(40), nullable = True)
	stripe_tokn	= Column(String(40), nullable = True)
   # 14) Buyer's Stripe Cust hash
    # 15) Buyer's Stripe Card hash



	def __init__(self, prof_hero, prof_buyer, datetime_s, datetime_f, cost, location, description, cust=None, card=None, state=None, flags=None): 
		self.prop_uuid = str(uuid.uuid4())
		self.prop_hero	= str(prof_hero)
		self.prop_buyer	= str(prof_buyer)
		self.prop_state	= state
		self.prop_flags = flags
		self.prop_count = 1
		self.prop_cost	= int(cost)
		self.prop_from = str(prof_buyer)

		self.prop_ts	= datetime_s
		self.prop_tf	= datetime_f
		self.prop_place	= location 
		self.prop_desc	= description

		self.prop_created = datetime.datetime.utcnow()
		self.prop_updated = datetime.datetime.utcnow()

		self.stripe_cust = cust
		self.stripe_card = card


	def update(self, prof_updated, updated_s=None, updated_f=None, update_cost=None, updated_place=None, updated_desc=None, updated_state=None, updated_flags=None): 
		self.prop_from = prof_updated
		self.prop_updated	= datetime.datetime.utcnow()
		self.prop_count		= self.prop_count + 1

		if (updated_s is not None): self.prop_ts = updated_s
		if (updated_f is not None): self.prop_tf = updated_f
		if (updated_cost is not None):	self.prop_cost	= int(updated_cost)
		if (updated_desc is not None):	self.prop_desc	= updated_desc
		if (updated_place is not None):	self.prop_place	= updated_place
		if (updated_state is not None):	self.prop_state = updated_state
		if (updated_flags is not None):	self.prop_flags = updated_flags


	def __repr__(self):
		return '<prop %r, Hero=%r, Buy=%r, State=%r>' % (self.prop_uuid, self.prop_hero, self.prop_buyer, self.prop_state)



class Timeslot(Base):
	__tablename__ = "timeslot"
	id         = Column(Integer, primary_key = True)
	profile_id = Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)			# SELLER
	creator_id = Column(String(40), ForeignKey('profile.heroid'), nullable=True,  index=True)			# BUYER (always a prop) 
	status     = Column(Integer, default=0)		#0 = free, #1 = bid on?  #2 = purchased, #4 = completed.   -1 = Removed/unlisted, #4 = canceled?


	location  = Column(String(1000), nullable = False)
	ts_begin  = Column(DateTime(),   nullable = False)
	ts_finish = Column(DateTime(),   nullable = False) # better to have this as a length of time?
	cost      = Column(Integer,    nullable = False)

	description = Column(String(3000),                            nullable = True)
	created = Column(DateTime(), nullable = False)
	updated = Column(DateTime(), nullable = False)
	challenge   = Column(String(40), nullable = False)	#use this to identify transaction instead of id 

	#booking = relationship("Booking", backref="timeslot", order_by="booking.id", lazy=False, uselist=False)
	#digital = Column(Boolean, default=0)#0 means the timeslot is not digital appointment

	def __init__(self, listing_profile, begin, finish, cost, desc, location, creator=None, status=TS_PROP_BY_HERO):
		self.profile_id  = listing_profile
		self.creator_id  = creator
		self.ts_begin    = begin
		self.ts_finish   = finish
		self.cost 		 = cost 
		self.description = desc
		self.location    = location 
		self.status      = status
		self.created = datetime.datetime.now()
		self.updated = datetime.datetime.now()
		self.challenge = str(uuid.uuid4())

	def __repr__(self):
		return '<timeslot %r, %r, %r, %r>' % (self.id, self.profile, self.ts_start, self.status)





class Appointment(Base):
	__tablename__ = "appointment2"

	id			= Column(Integer, primary_key = True)
	apptid		= Column(String(40), unique = True, primary_key = True, index=True)   #use challenge 
	buyer_prof	= Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)
	sellr_prof	= Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)			# if creator_id != profile_id; prop = True
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

	reviewOfBuyer	= Column(Integer, ForeignKey('review.id'), nullable = True)
	reviewOfSellr	= Column(Integer, ForeignKey('review.id'), nullable = True)


	#booking_id=Column(Integer, ForeignKey('booking.id'))
	#transaction_id=Column(Integer, ForeignKey('transaction.id'))
	#transaction_id=relationship("Transaction", backref="appointment", order_by="transaction.id", lazy=False, uselist=False)
	#review_id=relationship("Review", backref="appointment", order_by="review.id", lazy=False)


	def __init__ (self):
		pass

	def __repr__ (self):
		return '<appt2, b:%r, s:%r, C:%r>' % (self.buyer_prof, self.sellr_prof, self.cost)




class Transaction (Base):
	#stripe.api_key = "sk_test_nUrDwRPeXMJH6nEUA9NYdEJX"
	#stripe.Charge.retrieve("ch_2lAMeA9z956LjW", expand=["balance_transaction"])
	__tablename__ = "transaction"
	id	=		Column(Integer, primary_key=True)
#	purchaser_account = Column(String(40), ForeignKey('account.heroid'), nullable=False, index=True)
#	purchaser_profile = Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)
#	purchaser_customr = Column(String(20));	#charge.card.cust; stripe i

#	seller_account = Column(String(40), ForeignKey('account.heroid'), nullable=False, index=True)
#	seller_profile = Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)
#	seller_customr = Column(String(20));	#charge.cust; stripe i

#	stripe_charge_id			# charge_id, used to find transaction object
#	stripe_balance_transaction 	# transaction_info

	def __init__ (self):
		pass

	def __repr__ (self):
		return '<"transaction", %r>' % (self.id)




class BlockUser(Base):
	""" BlockUser provides a listing of every asynchronous blocking """ 
	__tablename__ = "BlockUser"
	id = Column(Integer,primary_key=True)
	profileId = Column(Integer,    nullable=False)
	filterId  = Column(Integer,    nullable=False)
	reason    = Column(String(80), nullable=False)

	def __init__(self, blocked_user_id, blocked_by_user_id, user_reason):
		self.profileId = blocked_by_user_id
		self.filterId  = blocked_user_id
		self.reason    = user_reason

	def __repr__(self):
		return '<BlockUser, %r ==>X %r>' % (self.filterId, self.profileId)



class Image(Base):
	__tablename__ = "image"

	id  = Column(Integer, primary_key=True)
	ts  = Column(DateTime,    nullable=False)
	fs  = Column(String(120))				#where file exists on FS
	img = Column(LargeBinary, nullable=True)
	profile = relationship("Profile", backref="image", lazy=False)


	def __init__(self, image):
		self.img = image
		self.tsc = datetime.datetime.now()

	def __repr__ (self):
		#return '< image, %r, %r>' % (self.img, self.ts) ... can we use profile ID/name?
		return '<image, %s>' % (self.ts)




class Organization(Base):
	__tablename__= "organization"
	id   = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False, unique=True)
	#CAH - do we need someone (account(s)) to maintain Organization info?
	#CAH - what about organization information like 'About IBM, or About Kaiser Permanente, Industry Info, Contact info to be verified?
	
	#CAH - add foreign key to Account.  
	#CAH - should organizations have contact info and/or extra information... listing profiles that want to be associated [obviously, must be 2-way] 

	def __init__ (self, org_name):
		self.name = org_name

	def __repr__ (self):
		return '<Organization, %r>' % (self.name)


class Industry(Base):
	__tablename__ = "industry"
	industries = ['Personal Wellness & Lifecoaches', 'Academia & Research', 'Artists, Architects, & Designers', 'Business and Finance', 'Education', 'Engineering and Technology',
		'Food', 'Government and Non-Profits', '--Healthcare and Law ', 'Hospitality', 'Finance, Accountants', 'Media & Entertainment',
		'Real Estate', 'Environment', 'Retail', 'Transportation Services', 'Travel & Leisure', 'Other']
	enumInd = [(str(k), v) for k, v in enumerate(industries)]

	id   = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False, unique=True)

	def __init__ (self, industry_name):
		self.name = industry_name

	def __repr__ (self):
		return '<industry, %r>' % (self.name)



class Review(Base):
	__tablename__ = "review"
	# insert into "Review"(profile, author, rating, ts, text) VALUES (7, 3, 4, '2013-09-16 16:05:17.073843', 'One bad mofo');

	ratePoints = ['',  '', '', '', '']
	enumRating = [(str(k), v) for k, v in enumerate(ratePoints)]

	id      = Column(Integer, primary_key = True, unique = True)
	heroid  = Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)
	author  = Column(String(40), ForeignKey('profile.heroid'), nullable=False, index=True)
	rating  = Column(Integer)
	ts      = Column(DateTime(), nullable = False) 				# CAH: date of appointment? -- why would we care when the review is posted?
	text    = Column(String(5000))
	twin    = Column(Integer, unique = True, nullable = True) 	#twin or sibling review

	#appointment_id=Column(Integer, ForeignKey('appointment.key'))
	#review_status=Column(Boolean, default=0)
	#review_flagged?

	def __init__ (self, reviewed_heroid, author_profile, rating, text):  #add rating
		self.heroid= reviewed_heroid
		self.author  = author_profile
		self.rating  = rating
		self.ts      = datetime.datetime.now()
		self.text    = text

	def __repr__ (self):
		return '<review %r, %r, %r, %r>' % (self.author, self.heroid, self.rating, self.text[:20])



#session table
# heroid, nonce, ts - gets updated every action.


# timeslot => appt.  Appt must match 1 to 1, take hash of prof.


