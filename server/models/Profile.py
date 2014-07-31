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



class Profile(Base):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	prof_id	= Column(String(40), primary_key=True, index=True)
	account	= Column(String(40), ForeignKey('account.userid'), nullable=False)
	prof_name	= Column(String(128), nullable=False)
	prof_vanity	= Column(String(128))
	#prof_skills	= relationship('skills', backref='profile', cascade='all,delete') 

	rating   = Column(Float(),   nullable=False, default=-1)
	reviews  = Column(Integer(), nullable=False, default=0)

	prof_img	= Column(String(128), default="no_pic_big.svg",	nullable=False) 
	prof_url	= Column(String(128), default='http://herotime.co')
	prof_bio	= Column(String(5000), default='About me')
	prof_tz		= Column(String(20))  #calendar export.
	prof_rate	= Column(Integer, nullable=False, default=40)

	industry	= Column(String(64))
	headline	= Column(String(128))
	location	= Column(String(64), nullable=False, default="Berkeley, CA")

	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")

	availability = Column(Integer, default=0)	

	#prof_img	= Column(Integer, ForeignKey('image.id'), nullable=True)  #CAH -> image backlog?
	#timeslots = relationship("Timeslot", backref='profile', cascade='all,delete', lazy=False, uselist=True, ##foreign_keys="[timeslot.profile_id]")

	def __init__ (self, name, acct):
		self.prof_id	= str(uuid.uuid4())
		self.prof_name	= name
		self.account	= acct
		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		tmp_headline = self.headline
		if (tmp_headline is not None):
			tmp_headline = tmp_headline[:20]
		return '<profile, %r, %r, %r, %r>' % (self.prof_id, self.prof_name, self.prof_rate, tmp_headline)


	@staticmethod
	def get_by_prof_id(profile_id):
		profile = None
		try:
			profile = Profile.query.filter_by(prof_id=profile_id).one()
		except NoResultFound as nrf:
			pass
		return profile


	@staticmethod
	def get_by_uid(uid):
		profile = None
		try:
			# cannot throw MultipleResultsFound, DB uniqueness
			profile = Profile.query.filter_by(account=uid).one()
		except NoResultFound as nrf:
			pass
		return profile


	@property
	def serialize(self):
		return {
			'account'	: str(self.account),
			'prof_id'	: str(self.prof_id),
			'prof_name'	: str(self.prof_name),
			'prof_img'	: str(self.prof_img),
			'prof_bio'	: str(self.prof_bio),
			'prof_rate'	: str(self.prof_rate),
			'headline'	: str(self.headline),
			'industry'	: str(self.industry),
		}



	def update_profile_image(self, newprof_img):
		# grab profile's current profile image.
		replace_img = Image.get_by_id(self.prof_img);
		if (replace_img is None): raise Exception("WTF, no profile image?!?")

		# update both images and profile
		replace_img.profile_image(False)
		newprof_img.profile_image(True)
		self.prof_img = newprof_img.img_id

		try:
			# save updated images, self
			db_session.add(replace_img)
			db_session.add(newprof_img)
			db_session.add(self)
			db_session.commit()
		except Exception as e:
			print type(e), e
			db_session.rollback()
		return self

