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



LESSON_FLAG_STARTED	= 0 		# User started to create a lesson
LESSON_FLAG_SAVED	= 1 		# User completed making the lesson but saved it before finished
LESSON_FLAG_PRIVATE	= 2 		# User completed making the lesson but left it private
LESSON_FLAG_ACTIVE	= 3 		# User completed making the lesson and made it active

LESSON_STATE_STARTED	= (0x1 << LESSON_FLAG_STARTED)	#1
LESSON_STATE_SAVED		= (0x1 << LESSON_FLAG_SAVED)	#2
LESSON_STATE_PRIVATE	= (0x1 << LESSON_FLAG_PRIVATE)	#4
LESSON_STATE_ACTIVE		= (0x1 << LESSON_FLAG_ACTIVE)	#8


# Profile states for teaching availability. 0 is when teaching has not been activated yet. 1 = flexible, 2 = specific

PROF_FLAG_AVAIL_NONE = 0
PROF_FLAG_AVAIL_FLEX = 1
PROF_FLAG_AVAIL_SPEC = 2

PROF_STATE_AVAIL_NONE = (0x1 << PROF_FLAG_AVAIL_NONE)
PROF_STATE_AVAIL_FLEX = (0x1 << PROF_FLAG_AVAIL_FLEX)
PROF_STATE_AVAIL_SPEC = (0x1 << PROF_FLAG_AVAIL_SPEC)

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

