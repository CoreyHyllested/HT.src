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


from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime
import uuid
import math



################################################################################
### LESSON FLAGS FIELD #########################################################
################################################################################
################################################################################
## 	BIT-RANGE		NAME			DETAILS
################################################################################
## 	0 - 3			State			Current state of the Lesson.
##	16				Approved		Flag.  Lesson Approved to be public.
##  17				Public			Flag.  Lesson currently is public.
##  20				Inappropriate	Lesson flagged as in apporoprate.
################################################################################
##  4-15,18,19,21-31				reserved
################################################################################


LESSON_STATE_INCOMPLETE	= 0
LESSON_STATE_COMPLETED	= 1
LESSON_STATE_SUBMITTED	= 2
LESSON_STATE_AVAILABLE	= 3
LESSON_STATE_MASK 		= (LESSON_STATE_INCOMPLETE | LESSON_STATE_COMPLETED | LESSON_STATE_SUBMITTED | LESSON_STATE_AVAILABLE)

LESSON_STATE_LOOKUP_TABLE = {
	LESSON_STATE_INCOMPLETE : 'INCOMPLETE',
	LESSON_STATE_COMPLETED  : 'COMPLETED',
	LESSON_STATE_SUBMITTED  : 'SUBMITTED',
	LESSON_STATE_AVAILABLE  : 'AVAILABLE',
}



# LESSON_FLAGS Field.
LESSON_BIT_INCOMPLETE	= 0 		# User started to create a lesson
LESSON_BIT_COMPLETED	= 1			# User saved a complete lesson
LESSON_BIT_SUBMITTED	= 2 		# User submitted a complete lesson
LESSON_BIT_AVAILABLE	= 3			# User started to create a lesson

LESSON_BIT_APPROVED			= 16 		# User started to create a lesson
LESSON_BIT_PUBLIC			= 17		# User completed making the lesson and made it public/active
LESSON_BIT_INAPPROPRIATE	= 20		# User completed making the lesson and made it public/active

LESSON_FLAG_APPROVED		= (0x1 << LESSON_BIT_APPROVED)		#00010000,	32K
LESSON_FLAG_PUBLIC			= (0x1 << LESSON_BIT_PUBLIC)		#00020000,	64K
LESSON_FLAG_INAPPROPRIATE	= (0x1 << LESSON_BIT_INAPPROPRIATE) #00100000,  512K


LESSON_RATE_PERHOUR = 0
LESSON_RATE_PERLESSON = 1



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
	lesson_flags	= Column(Integer, default=LESSON_STATE_INCOMPLETE)

	# Lesson Cost
	lesson_rate = Column(Integer)
	lesson_rate_unit = Column(Integer, default=LESSON_RATE_PERHOUR)
	lesson_group_rate = Column(Integer)
	lesson_group_rate_unit = Column(Integer, default=LESSON_RATE_PERHOUR)
	lesson_group_maxsize = Column(Integer)

	# Lesson Materials
	lesson_materials_needed = Column(String(5000))
	lesson_materials_provided = Column(String(5000))


	def __init__ (self, profile_id):
		self.lesson_id	= str(uuid.uuid4())
		self.lesson_profile	= profile_id
		self.lesson_created = dt.utcnow()
		self.lesson_flags = LESSON_STATE_INCOMPLETE


	def __repr__ (self):
		return '<Lesson: %r, %r, %r>' % (self.lesson_id, self.lesson_profile, self.lesson_title)

	def invalid_transition(msg = None):
		raise Exception('Invalid Transition ' + str(msg))


	def set_state(self, new_state):
		cur_state = (int(self.lesson_flags) & LESSON_STATE_MASK)
		nxt_state = (int(new_state) & LESSON_STATE_MASK)
		cstate_str = LESSON_STATE_LOOKUP_TABLE[cur_state]
		nstate_str = LESSON_STATE_LOOKUP_TABLE[nxt_state]

		if (cur_state == nxt_state):
			print "State unchanged."
			return

		print 'Lesson(' + self.lesson_id + ') change state: ' + str(cstate_str) + ' => ' + str(nstate_str)
		transitions = self.TRANSITION_MATRIX[cur_state]
		transition = transitions.get(nxt_state)
		if (transition is None):
			raise StateTransitionError(self.__class__, self.lesson_id, cur_state, nxt_state, self.lesson_flags, user_msg="No message for user")

		# execute transition function.
		success = transition(self, cur_state, nxt_state, msg = 'cah')
		if (success):
			flags = self.lesson_flags & (~LESSON_STATE_MASK)
			print 'Lesson.set_state()\tflags = ' + format(self.lesson_flags, '08X') + ' & ' + format(~LESSON_STATE_MASK, '08X') + ' = ' + format(flags, '08X')
			self.lesson_flags = flags | (new_state)
			print 'Lesson.set_state()\tflags = ' + format(flags,             '08X') + ' | ' + format(new_state,               '08X') + ' = ' + format(self.lesson_flags, '08X')


	def get_state(self):
		cur_state = (int(self.lesson_flags) & LESSON_STATE_MASK)
		cstate_str = LESSON_STATE_LOOKUP_TABLE[cur_state]
		return str(cstate_str)

	def get_duration_string(self):
		raw_duration = int(self.lesson_duration)
		if (raw_duration > 60):
			hours = math.floor(raw_duration / 60)
			minutes = int(math.fmod(raw_duration, 60))
			if (hours > 1):
				duration_str = str(hours) + " hours"
			else:
				duration_str = "1 hour"
			
			if (minutes > 0):
				duration_str += " and " + str(minutes) + " minutes"
		else:
			duration_str = str(raw_duration) + " minutes"

		return str(duration_str)


	################################################################################
	### LESSON STATE-CHANGE FUNCTIONS. #############################################
	################################################################################
	### The TRANSITION_MATRIX is a private matrix.  It contains all the valid     ###
	### transitions.  Each function should validate the input, and run all tasks ###
	### necessary for changing the state.  If a problem occurs, throw an Error.  ###
	################################################################################

	def __transition_incomplete_to_completed(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_incomplete_to_submitted(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_completed_to_submitted(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_completed_to_incomplete(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_submitted_to_incomplete(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_submitted_to_completed(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_submitted_to_available(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_available_to_completed(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True

	def __transition_available_to_incomplete(self, c_state, n_state, msg = None):
		print 'transitioning from ' + str(c_state) + ' to ' + str(n_state)
		return True		

	TRANSITION_MATRIX =	{	LESSON_STATE_INCOMPLETE	: { LESSON_STATE_COMPLETED	: __transition_incomplete_to_completed, 
														LESSON_STATE_SUBMITTED	: __transition_incomplete_to_submitted, },
							LESSON_STATE_COMPLETED	: { LESSON_STATE_SUBMITTED	: __transition_completed_to_submitted, 
														LESSON_STATE_INCOMPLETE : __transition_completed_to_incomplete, },
							LESSON_STATE_SUBMITTED	: { LESSON_STATE_COMPLETED	: __transition_submitted_to_completed,
														LESSON_STATE_AVAILABLE	: __transition_submitted_to_available, 
														LESSON_STATE_INCOMPLETE : __transition_submitted_to_incomplete, },
							LESSON_STATE_AVAILABLE	: { LESSON_STATE_COMPLETED	: __transition_available_to_completed, 
														LESSON_STATE_INCOMPLETE : __transition_available_to_incomplete, },
						}


	# Lesson Metadata
	lesson_updated	= Column(DateTime())
	lesson_created	= Column(DateTime(), nullable=False)
	lesson_flags	= Column(Integer, default=LESSON_STATE_INCOMPLETE)

	# Lesson Cost
	lesson_rate = Column(Integer)
	lesson_rate_unit = Column(Integer, default=LESSON_RATE_PERHOUR)
	lesson_group_rate = Column(Integer)
	lesson_group_rate_unit = Column(Integer, default=LESSON_RATE_PERHOUR)
	lesson_group_maxsize = Column(Integer)

	# Lesson Materials
	lesson_materials_needed = Column(String(5000))
	lesson_materials_provided = Column(String(5000))

	@property
	def serialize(self):
		duration_str = self.get_duration_string()
		print "duration_str is ",duration_str
		return {
			'lesson_id'			: str(self.lesson_id),
			'lesson_profile'	: self.lesson_profile,
			'lesson_description': str(self.lesson_description),
			'lesson_industry'	: str(self.lesson_industry),
			'lesson_avail'		: self.lesson_avail,
			'lesson_duration'	: self.lesson_duration,
			'lesson_duration_str'	: str(duration_str),
			'lesson_loc_option'	: self.lesson_loc_option,
			'lesson_address_1'	: str(self.lesson_address_1),
			'lesson_address_2'	: str(self.lesson_address_2),
			'lesson_city'		: str(self.lesson_city),
			'lesson_state'		: str(self.lesson_state),
			'lesson_zip'		: str(self.lesson_zip),
			'lesson_country'	: str(self.lesson_country),
			'lesson_address_details'	: str(self.lesson_address_details),
			'lesson_updated'	: str(self.lesson_updated),
			'lesson_created'	: str(self.lesson_created),
			'lesson_flags'		: self.lesson_flags,
			'lesson_rate'		: self.lesson_rate,
			'lesson_rate_unit'	: self.lesson_rate_unit,
			'lesson_group_rate'	: self.lesson_group_rate,
			'lesson_group_rate_unit'	: self.lesson_group_rate_unit,
			'lesson_group_maxsize'		: self.lesson_group_maxsize,
			'lesson_materials_needed'	: str(self.lesson_materials_needed),
			'lesson_materials_provided'	: str(self.lesson_materials_provided)
		}


	@staticmethod
	def state_name(state):
		return LESSON_STATE_LOOKUP_TABLE.get(state, None)


	@staticmethod
	def get_by_id(lid):
		lesson = None
		try:
			lesson = Lesson.query.filter_by(lesson_id=lid).one()
		except NoResultFound as nrf:
			pass
		return lesson


	@staticmethod
	def get_active_by_prof_id(profile_id):
		lessons = None
		try:
			lessons = Lesson.query.filter_by(lesson_profile=profile_id, lesson_flags=3).all()
		except NoResultFound as nrf:
			pass
		return lessons

	@staticmethod
	def get_enum_active_by_prof_id(profile_id):
		enumLessons = []
		try:
			lessons = Lesson.query.filter_by(lesson_profile=profile_id, lesson_flags=3).all()
			for lesson in lessons:
				enumLessons.append((lesson.lesson_id, lesson.lesson_title))

		except NoResultFound as nrf:
			pass
		return enumLessons
