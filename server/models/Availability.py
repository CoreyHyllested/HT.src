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
import uuid


DAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']


class Availability(Base):
	__tablename__ = "availability"
	avail_id		= Column(Integer, primary_key = True)
	avail_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	avail_created	= Column(DateTime(), nullable = False)
	avail_updated	= Column(DateTime(), nullable = False)

	avail_weekday	= Column(Integer,	 nullable = True)
	avail_start		= Column(DateTime,	 nullable = True)
	avail_finish	= Column(DateTime,	 nullable = True)

	avail_repeats	= Column(Integer,	 nullable = True)
	avail_timeout	= Column(DateTime,	 nullable = True)


	def __init__ (self, profile):
		self.avail_profile	= profile.prof_id
		self.avail_created	= dt.utcnow()
		self.avail_updated	= dt.utcnow()


	def __repr__ (self):
		return '<availablity %r>' % (self.avail_profile)



