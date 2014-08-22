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
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, Time, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import uuid


DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']


class Availability(Base):
	__tablename__ = "availability"
	avail_id		= Column(Integer, primary_key = True)
	avail_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	avail_created	= Column(DateTime(), nullable = False)
	avail_updated	= Column(DateTime(), nullable = False)

	avail_weekday	= Column(Integer,	 nullable = True)

	avail_repeats	= Column(Integer,	 nullable = True)
	avail_timeout	= Column(DateTime,	 nullable = True)
	
	avail_start		= Column(Time(),	 nullable = True)
	avail_finish	= Column(Time(),	 nullable = True)

	def __init__ (self, profile):
		self.avail_profile	= profile.prof_id
		self.avail_created	= dt.utcnow()
		self.avail_updated	= dt.utcnow()


	def __repr__ (self):
		return '<availablity %r>' % (self.avail_profile)

	@staticmethod
	def get_by_prof_id(profile_id):
		avail = None
		try:
			avail = Availability.query.filter_by(avail_profile=profile_id).all()
		except NoResultFound as nrf:
			pass
		return avail

	@staticmethod
	def get_avail_by_day(profile_id, day):
		start = None
		end = None
		try:
			avail = Availability.query.filter_by(avail_weekday=day, avail_profile=profile_id).first()
			print "get_avail_by_day: avail: ", avail
			start = avail.avail_start
			end = avail.avail_end
			print "get_avail_by_day: start: ", start
		except NoResultFound as nrf:
			pass
		return start, end


















