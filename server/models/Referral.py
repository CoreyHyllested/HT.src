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


from server import database
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
import uuid
from pprint import pprint as pp



class Referral(database.Model):
	__tablename__ = "referral"
	ref_uuid	= Column(String(40), primary_key=True, index=True, unique=True)
	ref_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)
	ref_content	= Column(String(200), nullable=False)	# referral content
	ref_project	= Column(String(128))					# project description
	ref_created = Column(DateTime(), nullable=False)

	def __init__ (self, profile, content, project=None):
		self.ref_uuid = str(uuid.uuid4())
		self.ref_profile = profile
		self.ref_content = content
		self.ref_project = project
		self.ref_created = dt.utcnow()

	def __repr__ (self):
		return '<Referral %r, %r, %r>'% (self.ref_uuid, self.ref_profile, self.ref_content[:20])

	@property
	def serialize(self):
		return {
			'ref_uuid'		: self.ref_uuid,
			'ref_profile'	: self.ref_profile,
			'ref_project'	: self.ref_project,
			'ref_content'	: self.ref_content
		}

	@staticmethod
	def get_by_refid(ref_id):
		referral = session.get('referrals', {}).get(ref_id, None)
		if (referral): return referral

		try:
			referral = Referral.query.filter_by(ref_uuid=ref_id).one()
		except NoResultFound as nrf: pass
		return referral




class RefList(database.Model):
	__tablename__ = "referral_list"
	list_uuid		= Column(String(40), primary_key=True, index=True, unique=True)
	list_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)
	list_project	= Column(String(40), ForeignKey('project.proj_id'))	# may be associated with a project
	list_name		= Column(String(40))								# may be given a name
	list_desc		= Column(String(120))								# may be given a description

	list_created	= Column(DateTime(), nullable=False)


	def __init__ (self, profile, project=None, name=None, desc=None):
		self.list_uuid = str(uuid.uuid4())
		self.list_profile = profile
		self.list_project = project
		self.list_name	= name
		self.list_desc	= desc

		self.list_created = dt.utcnow()


	@property
	def serialize(self):
		return {
			'list_id'		: self.list_uuid,
			'list_profile'	: self.list_profile,
			'list_project'	: self.list_project,
			'list_name'		: self.list_name,
			'list_desc'		: self.list_desc
		}


	@staticmethod
	def get_by_listid(list_id):
		reflist = session.get('lists', {}).get(list_id, None)
		if (reflist): return reflist

		try:
			reflist = RefList.query.filter_by(ref_uuid=list_id).one()
		except NoResultFound as nrf: pass
		return reflist



class RefListMemberMap(database.Model):
	__tablename__ = "referral_list_member_map"

	id				= Column(Integer, primary_key=True, unique=True)
	map_reflist	= Column(String(40), ForeignKey('referral_list.list_uuid'), nullable=False, index=True)
	map_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)		# member
	map_control	= Column(Integer, default=0)											# member's ACL

	def __init__ (self, reflist, profile, control):
		self.map_reflist = reflist
		self.map_profile = profile
		self.map_control = control



class RefListReferralMap(database.Model):
	__tablename__ = "referral_list_referral_map"

	id				= Column(Integer, primary_key=True, unique=True)
	map_reflist	= Column(String(40), ForeignKey('referral_list.list_uuid'), nullable=False, index=True)
	map_referal	= Column(String(40), ForeignKey('referral.ref_uuid'), nullable=False, index=True)

	def __init__ (self, reflist, referal):
		self.map_reflist = reflist
		self.map_referal = referal

