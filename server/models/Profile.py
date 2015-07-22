#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents. All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


from server import database
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from factory.fuzzy	 import *
from factory.alchemy import SQLAlchemyModelFactory

import uuid, urllib, hashlib, factory
from datetime import datetime as dt, timedelta
from pytz import timezone




# Profile states for teaching availability. 0 is when teaching has not been activated yet. 1 = flexible, 2 = specific
PROF_MENTOR_NONE = 0
PROF_MENTOR_FLEX = 1
PROF_MENTOR_SPEC = 2

PROF_FLAG_AVAIL_NONE = 0
PROF_FLAG_AVAIL_FLEX = 1
PROF_FLAG_AVAIL_SPEC = 2

PROF_STATE_AVAIL_NONE = (0x1 << PROF_FLAG_AVAIL_NONE)
PROF_STATE_AVAIL_FLEX = (0x1 << PROF_FLAG_AVAIL_FLEX)
PROF_STATE_AVAIL_SPEC = (0x1 << PROF_FLAG_AVAIL_SPEC)


class Profile(database.Model):
	""" Profile maintains information for each "instance" of a users identity.
		- i.e. Corey's 'DJ Core' profile, which is different from Corey's 'Financial Analyst' ident
	"""
	__tablename__ = "profile"
	prof_id	= Column(String(40), primary_key=True, index=True)
	account	= Column(String(40), ForeignKey('account.userid'), nullable=False)
	prof_name	= Column(String(128), nullable=False)

	prof_img	= Column(String(128), default="no_pic_big.svg",	nullable=False) 
	prof_url	= Column(String(128), default='https://soulcrafting.co')
	prof_bio	= Column(String(5000), default='About me')
	prof_tz		= Column(String(20))  #calendar export.
	prof_phone	= Column(String(20), nullable=True)
	prof_email	= Column(String(64), nullable=True)

	industry	= Column(String(64))
	headline	= Column(String(128))
	location	= Column(String(64), nullable=False, default="Boulder, CO")

	updated = Column(DateTime(), nullable=False, default = "")
	created = Column(DateTime(), nullable=False, default = "")

	def __init__(self, name, userid, email=None, phone=None,  area=None):
		#if area and (area.get('country_name') == 'Reserved' or area.get('country_name') == ''):
		#	area = None
		#else:
		#	area = area.get('region_name')

		print 'Profile: init \'' + str(area) + '\''
		self.prof_id	= str(uuid.uuid4())
		self.prof_name	= name
		self.account	= userid
		self.prof_phone = phone
		self.prof_email = email
		self.location	= area
		self.created	= dt.utcnow()
		self.updated	= dt.utcnow()


	def __repr__ (self):
		tmp_headline = self.headline
		if (tmp_headline is not None):
			tmp_headline = tmp_headline[:20]
		return '<profile, %r, %r, %r>' % (self.prof_id, self.prof_name, tmp_headline)


	@staticmethod
	def get_by_prof_id(profile_id):
		profile = None
		try:
			profile = Profile.query.filter_by(prof_id=profile_id).one()
		except NoResultFound as nrf: pass
		return profile


	@staticmethod
	def get_by_uid(uid):
		profile = None
		try:
			# cannot throw MultipleResultsFound, DB uniqueness
			profile = Profile.query.filter_by(account=uid).one()
		except NoResultFound as nrf: pass
		return profile


	@property
	def serialize(self):
		return {
			'account'	: str(self.account),
			'prof_id'	: str(self.prof_id),
			'prof_name'	: str(self.prof_name),
			'prof_img'	: str(self.prof_img),
			'prof_bio'	: str(self.prof_bio),
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
			database.session.add(replace_img)
			database.session.add(newprof_img)
			database.session.add(self)
			database.session.commit()
		except Exception as e:
			print type(e), e
			database.session.rollback()
		return self


	def gravatar_url(self):
		default_icon = "http://soulcrafting.co/static/img/favicon.png"
		gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.prof_email.lower()).hexdigest() + "?"
		gravatar_url += urllib.urlencode({'d':default_icon, 's':str(85)})
		return gravatar_url



#################################################################################
### FOR TESTING PURPOSES ########################################################
#################################################################################

class ProfileFactory(SQLAlchemyModelFactory):
	class Meta:
		model = Profile
		sqlalchemy_session = database.session

	prof_name = factory.Sequence(lambda n: u'TestProfile %d' % n)
	prof_acct = factory.fuzzy.FuzzyText(length=30, chars="1234567890-", prefix='test-acct-')

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		"""Override default '_create' with custom call"""

		name	= kwargs.pop('prof_name',	cls.prof_name)
		acct	= kwargs.pop('prof_acct',	cls.prof_acct)
		#print '_create: ', ds, ' - ', df
		#print '_create: ', cost
		#print '_create: ', location
		#print '_create: ', details

		obj = model_class(name, acct, *args, **kwargs)
		return obj
