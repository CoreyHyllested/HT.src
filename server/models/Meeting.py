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



class Meeting(Base):
	__tablename__ = "meeting"
	meet_id		= Column(String(40), primary_key=True)													# NonSequential ID
	meet_sellr	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE SELLER. The Hero
	meet_buyer	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)			# THE BUYER; requested hero.
	meet_owner	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)						# THE PROFILE who can make a decision. (to accept, etc)
	meet_state	= Column(Integer, nullable=False, default=APPT_STATE_PROPOSED,		index=True)			# Pure State (as in Machine)
	meet_flags	= Column(Integer, nullable=False, default=0)											# Attributes: Quiet?, Digital?, Run-Over Enabled?
	meet_count	= Column(Integer, nullable=False, default=0)											# Number of times vollied back and forth.
	meet_cost	= Column(Integer, nullable=False, default=0)											# Cost.
	meet_ts		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	meet_tf		= Column(DateTime(timezone=True),   nullable = False)									# Stored in UTC time
	meet_tz		= Column(String(32), nullable = False)
	meet_details	= Column(String(2048), nullable = False)
	meet_location	= Column(String(1024), nullable = False)	
	meet_created = Column(DateTime(), nullable = False)
	meet_updated = Column(DateTime(), nullable = False)
	meet_secured = Column(DateTime())
	meet_charged = Column(DateTime())

	charge_customer_id	= Column(String(40), nullable = True)	# stripe customer id
	charge_credit_card	= Column(String(40), nullable = True)	# stripe credit card
	charge_transaction	= Column(String(40), nullable = True)	# stripe transaction id
	charge_user_token	= Column(String(40), nullable = True)	# stripe charge tokn
	hero_deposit_acct	= Column(String(40), nullable = True)	# hero's stripe deposit account
	review_buyer = Column(String(40), ForeignKey('review.review_id'))	#TODO rename review_sellr
	review_sellr = Column(String(40), ForeignKey('review.review_id'))	#TODO rename review_buyer


	def __init__(self, hero, buyer, datetime_s, datetime_f, cost, location, description, token=None, customer=None, card=None, flags=None): 
		self.meet_id	= str(uuid.uuid4())
		self.meet_sellr	= str(hero)
		self.meet_buyer	= str(buyer)
		self.meet_cost	= int(cost)
		self.meet_from	= str(buyer)
		if (flags is not None): self.meet_flags = flags

		self.meet_ts	= datetime_s
		self.meet_tf	= datetime_f
		self.meet_tz	= 'US/Pacific'
		self.meet_location	= location 
		self.meet_details	= description

		self.charge_customer_id = customer
		self.charge_credit_card = card
		self.charge_user_token = token
		print 'Meeting(p_uid=%s, cost=%s, location=%s)' % (self.meet_id, cost, location)
		print 'Meeting(token=%s, cust=%s, card=%s)' % (token, customer, card)
		self.meet_created = dt.utcnow()
		self.meet_updated = dt.utcnow()


	def update(self, prof_updated, updated_s=None, updated_f=None, update_cost=None, updated_place=None, updated_desc=None, updated_state=None, updated_flags=None): 
		self.meet_from = prof_updated
		self.meet_updated	= dt.utcnow()
		self.meet_count		= self.meet_count + 1

		if (updated_s is not None): self.meet_ts = updated_s
		if (updated_f is not None): self.meet_tf = updated_f
		if (updated_cost is not None):	self.meet_cost	= int(updated_cost)
		if (updated_desc is not None):	self.meet_details = updated_desc
		if (updated_place is not None):	self.meet_location = updated_place
		if (updated_state is not None):	self.meet_state = updated_state
		if (updated_flags is not None):	self.meet_flags = updated_flags


	@staticmethod
	def get_by_id(meet_id):
		meeting = None
		try:
			# cannot raise MultipleResultsFound, meet_id is table unique.
			meeting = Meeting.query.filter_by(meet_id=meet_id).one()
		except NoResultFound as nrf:
			pass
		return meeting
	

	def set_flag(self, flag):
		if (flag <= APPT_FLAG_COMPLETE): raise Exception('Use set state to verify state change')
		self.meet_flags = (self.meet_flags | (0x1 << flag))


	def set_state(self, s_nxt, flag=None, uid=None, prof_id=None):
		s_cur = self.meet_state 
		flags = self.meet_flags
		valid = False
		error = None

		if ((s_nxt == APPT_STATE_TIMEDOUT) and (s_cur == APPT_STATE_PROPOSED)):
			valid = True
			s_nxt = APPT_STATE_REJECTED
			flags = set_flag(flags, APPT_FLAG_TIMEDOUT)

		elif ((s_nxt == APPT_STATE_REJECTED) and (s_cur == APPT_STATE_PROPOSED)):
			valid = True

			if (((prof_id != self.meet_sellr) and (prof_id != self.meet_buyer))):
				error = 'REJECTOR: ' + prof_id + " isn't HERO or USER"

		elif ((s_nxt == APPT_STATE_ACCEPTED) and (s_cur == APPT_STATE_PROPOSED)):
			valid = True
			print '\tMeeting.set_state()\tTransition from PROPOSED to ACCEPTED'
			if (self.meet_from == prof_id):
				error = 'LAST MODIFICATION and USER ACCEPTING PROPOSAL are same user: ' + str(uid)

			self.meet_secured = dt.utcnow()

#		elif ((s_nxt == APPT_STATE_CAPTURED) and (s_cur == APPT_STATE_ACCEPTED)):
#			if (flag == APPT_FLAG_HEROPAID): flags = set_flag(flags, APPT_FLAG_HEROPAID)
#			flags = set_flag(flags, APPT_FLAG_USERPAID)
#			self.meet_charged = dt.now()
		elif ((s_nxt == APPT_STATE_OCCURRED) and (s_cur == APPT_STATE_ACCEPTED)):
			valid = True
		elif ((s_nxt == APPT_STATE_CANCELED) and (s_cur == APPT_STATE_ACCEPTED)):
			valid = True
		elif ((s_nxt == APPT_STATE_COMPLETE) and (s_cur == APPT_STATE_OCCURRED)):
			valid = True
		elif ((s_nxt == APPT_STATE_DISPUTED) and (s_cur == APPT_STATE_COMPLETE)):
			valid = True
		else:
			# Invalid Transition; create a SANITIZED MESSAGE for problems
			error = 'The MEETING is in an INVALID STATE for this transaction'
			if (s_nxt == s_cur):
				error = 'Meeting already in STATE (' + str(s_cur) +  ')'

		if (error or not valid):
			raise StateTransitionError(self.__class__, self.meet_id, self.meet_state, s_nxt, flags, user_msg=error)

		self.meet_state = s_nxt
		self.meet_flags = flags
		self.meet_updated = dt.utcnow()
		if (self.meet_state == APPT_STATE_ACCEPTED): self.transition_to_ACCEPTED()



	def transition_to_ACCEPTED(self):
		print '\tMeeting.transition_to_ACCEPTED()'



	def accepted(self): return (self.meet_state == APPT_STATE_ACCEPTED)
	def canceled(self): return (self.meet_state == APPT_STATE_CANCELED)
	def occurred(self): return (self.meet_state == APPT_STATE_OCCURRED)

	def get_meet_ts(self, tz=None):
		zone = self.meet_tz or 'US/Pacific'
		return self.meet_ts.astimezone(timezone(zone))

	def get_meet_tf(self, tz=None):
		zone = self.meet_tz or 'US/Pacific'
		return self.meet_tf.astimezone(timezone(zone))

	def get_duration(self):
		return (self.meet_tf - self.meet_ts)

	def get_duration_in_hours(self):
		td = self.meet_tf - self.meet_ts
		td_days = td.days
		td_hour	= (td.seconds / 3600)
		td_mins = (td.seconds % 3600) / 60

		elapsed	= ''
		if (td_hour > 1):
			elapsed = elapsed + str(td_hour) + ' hours'
		elif (td_hour == 1):
			elapsed = elapsed + str(td_hour) + ' hour'

		if (td_mins != 0):
			if (td_hour != 0): elapsed = elapsed + ' and '
			elapsed = elapsed + str(td_mins) + ' mins'
		return elapsed


	def get_description_html(self):
		description = self.meet_desc.replace('\n', '<br>')
		return description
			

	def accept_url(self): return str('https://127.0.0.1:5000/meeting/accept?meet_id=' + self.meet_id)
	def reject_url(self): return str('https://127.0.0.1:5000/meeting/reject?meet_id=' + self.meet_id)
	def __repr__(self):	return '<meet %r, Hero=%r, Buy=%r, State=%r>' % (self.meet_id, self.meet_sellr, self.meet_buyer, self.meet_state)


	@property
	def serialize(self):
		return {
			'meet_id'		: self.meet_id,
			'meet_sellr'	: self.meet_sellr,
			'meet_buyer'	: self.meet_buyer,
			'meet_state'	: self.meet_state,
			'meet_flags'	: self.meet_flags,
			'meet_cost'		: self.meet_cost,
			'meet_updated'	: self.meet_updated.strftime('%A, %b %d, %Y %H:%M %p')
		}


