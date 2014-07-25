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


from __future__ import absolute_import
from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
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
		review = None
		try:
			review = Review.query.filter_by(review_id=rev_id).one()
		except NoResultFound as nrf:
			pass
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
			raise StateTransitionError(self.__class__, self.review_id, self.rev_status, s_nxt, user_msg=msg)

		self.rev_status = s_nxt
		self.rev_updated = dt.utcnow()


	def get_review_url(self):
		return '/review/new/' + str(self.review_id)




