from server import db
import datetime, uuid


TS_PROP_BY_HERO = 0
TS_PROP_BY_USER = 1
TS_USER_ACCEPTD = 2
TS_PROP_PURCHSD = 2
TS_PROP_COMPLTD = 4

TS_HERO_REMOVED = -1
TS_APP_CANCELED = -2

APPT_DISPUTED		= -2
APPT_CANCELED		= -1 
APPT_HAVE_AGREEMENT	=  0
APPT_CARD_CAPTURED	=  1   #money is captured, heros will get paid
APPT_SEND_REVIEWS	=  2   #24 hours after meeting, send reviews
APPT_POST_REVIEWS	=  3   #30 days after meeting, post reviews


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
 


class Account(db.Model):
	"""Account maintains identity information each individual."""
	__tablename__ = "account"
	USER_UNVERIFIED = 0
	USER_ACTIVE		= 1
	USER_INACTIVE	= -1
	USER_BANNED		= -2

	userid  = db.Column(db.String(40), primary_key=True,            unique=True)
	email   = db.Column(db.String(120), nullable=False, index=True, unique=True)
	name    = db.Column(db.String(120), nullable=False)
	pwhash	= db.Column(db.String(120), nullable=False)
	status  = db.Column(db.Integer,		nullable=False, default=USER_UNVERIFIED)   
	source  = db.Column(db.Integer,		nullable=False, default=0)   # 0 = User created id here. Else: Linkedin = 1, FB = 2, Google = 3, Twitter = 4, StackOverflow = 5
	dob     = db.Column(db.DateTime())
	created = db.Column(db.DateTime())
	sec_question = db.Column(db.String(120))
	sec_answer   = db.Column(db.String(50))
	# optional phone number?
	# add stripe ID
	# add stripe token?

	# all user profiles
	profiles = db.relationship('Profile', cascade='all,delete', uselist=False, lazy=False)

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



#class Oauth(db.Model):
#	__tablename__ = "oauth_accounts"
#	id      = db.Column(db.Integer, primary_key = True)
#	account = db.Column(db.String(40), db.ForeignKey('account.userid'), nullable=False, index=True)
#	oa_name = db.Column(db.String(40),									nullable=False)
#	oa_user = db.Column(db.String(40),									nullable=False)
#	token   = db.Column(db.String(120),									nullable=False)



class OauthStripe(db.Model):
	""" Account for maintaining stripe info """ 

	__tablename__ = "oauth_stripe"
	id      = db.Column(db.Integer, primary_key = True)
	account = db.Column(db.String(40), db.ForeignKey('account.userid'), nullable=False, index=True)
	stripe  = db.Column(db.String(40), nullable=False, index=True)
	token   = db.Column(db.String(40), nullable=False)
	pubkey  = db.Column(db.String(40), nullable=False)

	def __init__ (self, account):
		self.account = account

	def __repr__ (self):
		return '<oauth_stripe, %r %r %r>' % (self.account, self.stripe, self.token)
		



class Profile(db.Model):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	id       = db.Column(db.Integer, primary_key=True)	
	heroid   = db.Column(db.String(40), index=True, unique=True, nullable=False)
	account  = db.Column(db.String(40), db.ForeignKey('account.userid'), nullable=False)
	name     = db.Column(db.String(120), 								 nullable=False)
	imgURL	 = db.Column(db.String(120), default="no_pic_big.svg",		 nullable=False) 
	skills	 = db.Column(db.String(120), 								 nullable=True) #CSV => #x, #y, #z
	vanity   = db.Column(db.String(100), 								 nullable=True)

	rating   = db.Column(db.Float(),   nullable=False, default=-1)
	reviews  = db.Column(db.Integer(), nullable=False, default=0)

	img      = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=True)  #CAH -> image backlog?
	url      = db.Column(db.String(120),  default='http://herotime.co')
	bio      = db.Column(db.String(5000), default='About me')

	industry   = db.Column(db.String(50), nullable=True)
	headline   = db.Column(db.String(50), nullable=True)
	location   = db.Column(db.String(50), nullable=False, default="Berkeley, CA")
	baserate   = db.Column(db.Integer,    nullable=False, default=100)
	negotiable = db.Column(db.Boolean,	  nullable=False, default=True)

#    timeslots = db.relationship("Timeslot", backref='profile', cascade='all,delete', uselist=True, lazy=False)
	#timeslots = db.relationship("Timeslot", backref='profile', cascade='all,delete', lazy=False, uselist=True, ##foreign_keys="[timeslot.profile_id]")
	
	zipcode  = db.Column(db.Integer)
	timezone = db.Column(db.String(20))  #calendar export.
	updated = db.Column(db.DateTime(), nullable=False, default = datetime.datetime.now())
	created = db.Column(db.DateTime(), nullable=False, default = datetime.datetime.now())

	def __init__ (self, profile_name, acct):
		self.name = profile_name
		self.heroid  = str(uuid.uuid4())
		self.account = acct

	def __repr__ (self):
		return '<profile, %r, %r, %r, %r>' % (self.heroid, self.name, self.baserate, self.headline[:20])
		


class Timeslot(db.Model):
	__tablename__ = "timeslot"
	id         = db.Column(db.Integer, primary_key = True)
	profile_id = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
	creator_id = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=True,  index=True)			# if creator_id != profile_id; proposal = True
	status     = db.Column(db.Integer, default=0)		#0 = free, #1 = bid on?  #2 = purchased, #4 = completed.   -1 = Removed/unlisted, #4 = canceled?


	location  = db.Column(db.String(1000), nullable = False)
	ts_begin  = db.Column(db.DateTime(),   nullable = False)
	ts_finish = db.Column(db.DateTime(),   nullable = False) # better to have this as a length of time?
	cost      = db.Column(db.Integer,    nullable = False)

	description = db.Column(db.String(3000),                            nullable = True)
	created = db.Column(db.DateTime(), nullable = False)
	updated = db.Column(db.DateTime(), nullable = False)
	challenge   = db.Column(db.String(40), nullable = False)	#use this to identify transaction instead of id 

	#booking = db.relationship("Booking", backref="timeslot", order_by="booking.id", lazy=False, uselist=False)
	#digital = db.Column(db.Boolean, default=0)#0 means the timeslot is not digital appointment

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





class Appointment(db.Model):
	__tablename__ = "appointment2"

	id			= db.Column(db.Integer, primary_key = True)
	apptid		= db.Column(db.String(40), unique = True, primary_key = True, index=True)   #use challenge 
	buyer_prof	= db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
	sellr_prof	= db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)			# if creator_id != profile_id; proposal = True
	status		= db.Column(db.Integer, default=0)		#0 = free, #1 = bid on?  #2 = purchased, #4 = completed.   -1 = Removed/unlisted, #4 = canceled?

	location	= db.Column(db.String(1000), nullable = False)
	ts_begin	= db.Column(db.DateTime(),	 nullable = False)
	ts_finish 	= db.Column(db.DateTime(),	 nullable = False) # better to have this as a length of time?
	cost	= db.Column(db.Integer,	nullable = False)
	paid	= db.Column(db.Boolean,	default = False)
	cust	= db.Column(db.String(20),	nullable = False)

	description = db.Column(db.String(3000), nullable = True)
	transaction	= db.Column(db.String(40), nullable = True)	#stripe transaction 
	created		= db.Column(db.DateTime(), nullable = False)
	updated		= db.Column(db.DateTime(), nullable = False, default = datetime.datetime.now())
	agreement	= db.Column(db.DateTime(), nullable = False, default = datetime.datetime.now())

	reviewOfBuyer	= db.Column(db.Integer, db.ForeignKey('review.id'), nullable = True)
	reviewOfSellr	= db.Column(db.Integer, db.ForeignKey('review.id'), nullable = True)


	#booking_id=db.Column(db.Integer, ForeignKey('booking.id'))
	#transaction_id=db.Column(db.Integer, ForeignKey('transaction.id'))
	#transaction_id=relationship("Transaction", backref="appointment", order_by="transaction.id", lazy=False, uselist=False)
	#review_id=relationship("Review", backref="appointment", order_by="review.id", lazy=False)


	def __init__ (self):
		pass

	def __repr__ (self):
		return '<appt2, b:%r, s:%r, C:%r>' % (self.buyer_prof, self.sellr_prof, self.cost)




class Transaction (db.Model):
	#stripe.api_key = "sk_test_nUrDwRPeXMJH6nEUA9NYdEJX"
	#stripe.Charge.retrieve("ch_2lAMeA9z956LjW", expand=["balance_transaction"])
	__tablename__ = "transaction"
	id	=		db.Column(db.Integer, primary_key=True)
#	purchaser_account = db.Column(db.String(40), db.ForeignKey('account.heroid'), nullable=False, index=True)
#	purchaser_profile = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
#	purchaser_customr = db.Column(db.String(20));	#charge.card.cust; stripe i

#	seller_account = db.Column(db.String(40), db.ForeignKey('account.heroid'), nullable=False, index=True)
#	seller_profile = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
#	seller_customr = db.Column(db.String(20));	#charge.cust; stripe i

#	stripe_charge_id			# charge_id, used to find transaction object
#	stripe_balance_transaction 	# transaction_info

	def __init__ (self):
		pass

	def __repr__ (self):
		return '<"transaction", %r>' % (self.id)




class BlockUser(db.Model):
	""" BlockUser provides a listing of every asynchronous blocking """ 
	__tablename__ = "BlockUser"
	id = db.Column(db.Integer,primary_key=True)
	profileId = db.Column(db.Integer,    nullable=False)
	filterId  = db.Column(db.Integer,    nullable=False)
	reason    = db.Column(db.String(80), nullable=False)

	def __init__(self, blocked_user_id, blocked_by_user_id, user_reason):
		self.profileId = blocked_by_user_id
		self.filterId  = blocked_user_id
		self.reason    = user_reason

	def __repr__(self):
		return '<BlockUser, %r ==>X %r>' % (self.filterId, self.profileId)



class Image(db.Model):
	__tablename__ = "image"

	id  = db.Column(db.Integer, primary_key=True)
	ts  = db.Column(db.DateTime,    nullable=False)
	fs  = db.Column(db.String(120))				#where file exists on FS
	img = db.Column(db.LargeBinary, nullable=True)
	profile = db.relationship("Profile", backref="image", lazy=False)


	def __init__(self, image):
		self.img = image
		self.tsc = datetime.datetime.now()

	def __repr__ (self):
		#return '< image, %r, %r>' % (self.img, self.ts) ... can we use profile ID/name?
		return '<image, %s>' % (self.ts)




class Organization(db.Model):
	__tablename__= "organization"
	id   = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False, unique=True)
	#CAH - do we need someone (account(s)) to maintain Organization info?
	#CAH - what about organization information like 'About IBM, or About Kaiser Permanente, Industry Info, Contact info to be verified?
	
	#CAH - add foreign key to Account.  
	#CAH - should organizations have contact info and/or extra information... listing profiles that want to be associated [obviously, must be 2-way] 

	def __init__ (self, org_name):
		self.name = org_name

	def __repr__ (self):
		return '<Organization, %r>' % (self.name)


class Industry(db.Model):
	__tablename__ = "industry"
	industries = ['Personal Wellness & Lifecoaches', 'Academia & Research', 'Artists, Architects, & Designers', 'Business and Finance', 'Education', 'Engineering and Technology',
		'Food', 'Government and Non-Profits', '--Healthcare and Law ', 'Hospitality', 'Finance, Accountants', 'Media & Entertainment',
		'Real Estate', 'Environment', 'Retail', 'Transportation Services', 'Travel & Leisure', 'Other']
	enumInd = [(str(k), v) for k, v in enumerate(industries)]

	id   = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80), nullable = False, unique=True)

	def __init__ (self, industry_name):
		self.name = industry_name

	def __repr__ (self):
		return '<industry, %r>' % (self.name)



class Review(db.Model):
	__tablename__ = "review"
	# insert into "Review"(profile, author, rating, ts, text) VALUES (7, 3, 4, '2013-09-16 16:05:17.073843', 'One bad mofo');

	ratePoints = ['',  '', '', '', '']
	enumRating = [(str(k), v) for k, v in enumerate(ratePoints)]

	id      = db.Column(db.Integer, primary_key = True, unique = True)
	heroid  = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
	author  = db.Column(db.String(40), db.ForeignKey('profile.heroid'), nullable=False, index=True)
	rating  = db.Column(db.Integer)
	ts      = db.Column(db.DateTime(), nullable = False) 				# CAH: date of appointment? -- why would we care when the review is posted?
	text    = db.Column(db.String(5000))
	twin    = db.Column(db.Integer, unique = True, nullable = True) 	#twin or sibling review

	#appointment_id=db.Column(db.Integer, ForeignKey('appointment.key'))
	#review_status=db.Column(db.Boolean, default=0)
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


