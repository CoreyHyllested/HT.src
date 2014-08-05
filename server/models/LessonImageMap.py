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



IMG_FLAG_PROFILE = 0	# A Profile Image
IMG_FLAG_FLAGGED = 1	# The current Profile Img, needed? -- saved in profile, right?
IMG_FLAG_VISIBLE = 2	# Image is visible or shown.  Maybe flagged, deleted, or not ready yet.
IMG_FLAG_SELLERPROF = 3	# Image is a Seller's Profile Image.

IMG_STATE_PROFILE = (0x1 << IMG_FLAG_PROFILE)
IMG_STATE_FLAGGED = (0x1 << IMG_FLAG_FLAGGED)
IMG_STATE_VISIBLE = (0x1 << IMG_FLAG_VISIBLE)
IMG_STATE_SELLERPROF = (0x1 << IMG_FLAG_VISIBLE)



class LessonImageMap(Base):
	__tablename__ = "image_lesson_map"					#TODO rename 'lesson_image_map
	id			= Column(Integer, primary_key = True)	#TODO rename map_id
	map_image	= Column(String(64),  nullable=False, index=True)
	map_lesson	= Column(String(40),  nullable=False, index=True)
	map_prof	= Column(String(40),  nullable=True,  index=True)
	map_comm	= Column(String(256), nullable=True)
	map_order	= Column(Integer, 	  nullable=False)
	#map_flags	: use flags in Lesson and Image???
	#map_created: use timestamp in Lesson and Image???

	def __init__(self, img, lesson, profile, comment=None):
		self.map_image	= img
		self.map_lesson = lesson
		self.map_prof	= profile
		self.map_comm	= comment
		self.map_order	= -1
		print 'LessonImageMap.  created'


	def __repr__(self):
		print '<li_map %r %r>' % (self.map_lesson, self.map_image)


	@staticmethod
	def get_images_for_lesson(lesson_id):
		images = LessonImageMap.query.filter_by(map_lesson=lesson_id).all()
		print 'LessonImageMap.get_images_for_lesson_id(' + str(lesson_id) + '): ', len(images)
		return images


	@staticmethod
	def exists(image_id, lesson_id):
		images = LessonImageMap.get_images_for_lesson(lesson_id)
		for img in images:
			if (img.map_image == image_id): return True
		return False


	@property
	def serialize(self):
		return {
			'img_id'		: self.map_image,	# used by 'add_lesson.js'
			'img_comment'	: self.map_comm,	# used by 'add_lesson.js'
			'img_order'		: self.map_order,	# used by 'add_lesson.js'
			'img_lesson'	: self.map_lesson,	#img_lesson
			'img_profile'	: self.map_prof,	#img_profile
			#img_created
			#img_flags
		}



