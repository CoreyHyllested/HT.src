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

	avail_weekday	= Column(Integer)	# general day (0-6)
	avail_repeats	= Column(Integer)	# should be boolean?
	avail_timeout	= Column(DateTime)	# not used?
	avail_start		= Column(Time())
	avail_finish	= Column(Time())
	avail_project	= Column(String(40), ForeignKey('project.proj_id'), nullable=True, index=True, unique=True)

	def __init__ (self, profile, project_id=None, day=None, time_start=None):
		self.avail_profile	= profile.prof_id
		self.avail_project	= project_id
		self.avail_weekday	= day 
		self.avail_start	= time_start

		self.avail_created	= dt.utcnow()
		self.avail_updated	= dt.utcnow()
		


	def __repr__ (self):
		return '<availablity %r %r %r>' % (self.avail_profile, self.avail_project, self.avail_weekday)


	@staticmethod
	def get_by_prof_id(profile_id):
		avail = None
		try:
			avail = Availability.query.filter_by(avail_profile=profile_id).all()
		except NoResultFound as nrf:
			pass
		return avail



	@staticmethod
	def get_project_scheduled_time(project_id):
		availability = None
		try:
			availability = Availability.query.filter_by(avail_project=project_id).one()
		except NoResultFound as nrf:
			pass
		return availability



	@staticmethod
	def get_avail_by_day(profile_id, day):
		start = None
		finish = None
		try:
			avail = Availability.query.filter_by(avail_weekday=day, avail_profile=profile_id).first()
			print "get_avail_by_day: avail: ", avail
			start = avail.avail_start
			finish = avail.avail_finish
			print "get_avail_by_day: start: ", start
			print "get_avail_by_day: finish: ", finish
		except NoResultFound as nrf:
			pass
		return start, finish



	@staticmethod
	def get_avail_days(profile_id):
		days = [0,1,2,3,4,5,6]
		availdays = []
		try:
			for day in days:
				dayavail = Availability.query.filter_by(avail_weekday=day, avail_profile=profile_id).all()
				print "get_avail_by_day: day: ", day, " avail: ", str(dayavail)
				if dayavail:
					availdays.append(day)
		except NoResultFound as nrf:
			pass
		return availdays


















