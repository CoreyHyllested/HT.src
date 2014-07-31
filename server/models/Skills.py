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



class Skills(Base):
	__tablename__ = "skills"
	skill_id   = Column(Integer, primary_key = True)
	skill_name = Column(String(80), nullable = False)
	skill_prof = Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)

	def __init__ (self, name, prof):
		self.skill_name = name
		self.skill_prof = prof

	def __repr__ (self):
		return '<skill %r>' % (self.name)




