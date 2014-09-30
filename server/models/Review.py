#################################################################################
# Copyright (C) 2014 Insprite, LLC.
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
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import uuid



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


