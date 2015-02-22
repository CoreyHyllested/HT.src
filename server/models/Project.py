#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting.  Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm import relationship, backref
from factory.fuzzy	 import *
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime as dt, timedelta
from pytz import timezone
import uuid, factory


class Project(Base):
	""" Project maintains information for each project.  """
	__tablename__ = "project"
	proj_id	= Column(String(40), primary_key=True, index=True)
	account	= Column(String(40), ForeignKey('account.userid'), nullable=False)
	proj_name	= Column(String(128), nullable=False)
	proj_addr	= Column(String(256))
	proj_desc	= Column(String(5000))
	timeline = Column(String(256))
	proj_min = Column(Integer())
	proj_max = Column(Integer())
	proj_review = Column(Integer(), default=-1)

	contact = Column(String(20))	# phone number
	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")

	availability = Column(Integer(), default=0)	
	#timeslots = relationship('Availability', backref='project', cascade="all, delete")

	def __init__(self, name, acct, area=None):
		if (area and area.get('country_name') == 'Reserved'): area = 'The Internet'
		if (area and area.get('region_name')  == ''): area = None
		print 'Project: init \'' + str(area) + '\''
		self.proj_id	= str(uuid.uuid4())
		self.proj_name	= name
		self.account	= acct
		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		desc = self.proj_desc
		if (desc is not None): desc = desc[:20]
		return '<project, %r, %r, %r-%r, %r>' % (self.proj_id, self.proj_name, self.proj_min, self.proj_max, desc)


	@staticmethod
	def get_by_proj_id(project_id):
		project = None
		try:
			project = Project.query.filter_by(proj_id=project_id).one()
		except NoResultFound as nrf:
			pass
		return project


	@property
	def serialize(self):
		return {
			'account'	: str(self.account),
			'proj_id'	: str(self.proj_id),
			'proj_name'	: str(self.proj_name),
			'proj_desc'	: str(self.proj_desc),
			'proj_min'	: str(self.proj_min),
			'proj_max'	: str(self.proj_max),
		}




#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class ProjectFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Project
		sqlalchemy_session = db_session

	proj_name = factory.Sequence(lambda n: u'TestProject %d' % n)
	proj_acct = factory.fuzzy.FuzzyText(length=30, chars="1234567890-", prefix='test-acct-')

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		name	= kwargs.pop('proj_name',	cls.proj_name)
		acct	= kwargs.pop('proj_acct',	cls.proj_acct)
		#print '_create: ', ds, ' - ', df
		#print '_create: ', cost
		#print '_create: ', location
		#print '_create: ', details

		obj = model_class(name, acct, *args, **kwargs)
		return obj
