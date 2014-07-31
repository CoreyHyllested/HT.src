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



class Industry(Base):
	__tablename__ = "industry"
	industries = ['Art & Design', 'Athletics & Sports', 'Beauty & Style', 'Food', 'Music', 'Spirituality',  'Technology', 'Travel & Leisure', 'Health & Wellness', 'Other']
	enumInd = [(str(k), v) for k, v in enumerate(industries)]
	enumInd.insert(0, (-1, 'All Industries'))
	enumInd2 = [(str(k), v) for k, v in enumerate(industries)]

	id   = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False, unique=True)

	def __init__ (self, industry_name):
		self.name = industry_name

	def __repr__ (self):
		return '<industry, %r>' % (self.name)



