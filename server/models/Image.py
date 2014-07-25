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


from __future__ import absolute_import
from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime
import uuid


IMG_FLAG_PROFILE = 0	# A Profile Image
IMG_FLAG_FLAGGED = 1	# The current Profile Img, needed? -- saved in profile, right?
IMG_FLAG_VISIBLE = 2	# Image is visible or shown.  Maybe flagged, deleted, or not ready yet.
IMG_FLAG_SELLERPROF = 3	# Image is a Seller's Profile Image.

IMG_STATE_PROFILE = (0x1 << IMG_FLAG_PROFILE)
IMG_STATE_FLAGGED = (0x1 << IMG_FLAG_FLAGGED)
IMG_STATE_VISIBLE = (0x1 << IMG_FLAG_VISIBLE)
IMG_STATE_SELLERPROF = (0x1 << IMG_FLAG_VISIBLE)



class Image(Base):
	""" Table of all Images on Insprite.  Used by LessonImageMap and Profile """
	__tablename__ = "image"

	img_id = Column(String(64), primary_key=True)
	img_profile = Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	img_comment = Column(String(256))
	img_created = Column(DateTime())
	img_flags	= Column(Integer, default=0)
	img_order	= Column(Integer, default=0, nullable=False)
	img_lesson	= Column(String(256))


	def __init__(self, imgid, prof_id, comment=None, lesson=None):
		self.img_id  = imgid
		self.img_profile = str(prof_id)
		self.img_comment = comment
		self.img_lesson = lesson
		self.img_created = dt.utcnow()
		self.img_flags = IMG_STATE_VISIBLE

	def __repr__ (self):
		return '<image %s %s>' % (self.img_id, self.img_comment[:20])


	@staticmethod
	def get_by_id(image_name):
		try:
			img = None
			img = Image.query.filter_by(img_id=image_name).first()
		except MultipleResultsFound as mrf:
			print 'Never Happen Error: caught exception looking for img_id ', image_name
		except NoResultFound as nrf:
			pass
		return img


	@property
	def serialize(self):
		return {
			'img_id'		: self.img_id,
			'img_profile'	: self.img_profile,
			'img_comment'	: self.img_comment,
			'img_created'	: self.img_created,
			'img_flags'		: self.img_flags,
			'img_order'		: self.img_order,
		}


	def profile_image(self, new_value):
		flags = self.img_flags
		#setting =  (flags | (       IMG_STATE_PROFILE))
		#clearing = (flags & (~0x0 ^ IMG_STATE_PROFILE))
		flags = (new_value) and (flags | (IMG_STATE_PROFILE)) or (flags & (~0x0 ^ IMG_STATE_PROFILE))
		#print 'update()\tProfile.update_profile_image()\timg_flags = [Setting] ' + format(flags, '08X') + ' | ' + format(IMG_STATE_PROFILE, '08X') + ' = ' + format(setting, '08X')
		#print 'update()\tProfile.update_profile_image()\timg_flags = [Clearng] ' + format(flags, '08X') + ' & ' + format(~0x0 ^ IMG_STATE_PROFILE, '08X') + ' = ' + format(clearing, '08X')
		#print 'update()\tProfile.update_profile_image()\timg_flags = (' + str(new_value) + ') = ' + format(flags, '08x')
		self.img_flags = flags
		return (self.img_flags & IMG_STATE_PROFILE)


