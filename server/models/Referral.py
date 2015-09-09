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


import uuid
from datetime import datetime as dt, timedelta

from server import database
from server.models.Business	import *
from server.models.Location	import *
from server.models.shared	import ReferralFlags
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey, Column, String, Integer, DateTime
from sqlalchemy.orm import aliased, relationship, backref
from sqlalchemy.orm.exc import DetachedInstanceError


class Referral(database.Model):
	__tablename__ = "referral"
	ref_uuid		= Column(String(40), primary_key=True, index=True)
	ref_business	= Column(String(40), ForeignKey('business.bus_id'), nullable=False)
	ref_profile		= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)
	ref_content		= Column(String(200), nullable=False)	# referral content
	ref_project		= Column(String(128))					# project description

	ref_flags	= Column(Integer)
	ref_created = Column(DateTime(), nullable=False)


	def __init__ (self, bus_id, profile, content, project=None):
		self.ref_uuid = str(uuid.uuid4())
		self.ref_business = bus_id
		self.ref_profile = profile.prof_id
		self.ref_content = content
		self.ref_project = project
		self.ref_flags	 = 0
		self.ref_created = dt.utcnow()


	def __repr__ (self):
		return '<Referral %r, %r, %r>'% (self.ref_uuid, self.ref_business, self.ref_content[:20])

	def authored_by(self, profile):
		return (profile and profile.prof_id == self.ref_profile)

	def invalid(self):
		return ReferralFlags.test_invalid(self.ref_flags)

	def set_invalid(self):
		self.ref_flags = ReferralFlags.set_invalid(self.ref_flags)
		return self.ref_flags

	def set_valid(self):
		self.ref_flags = ReferralFlags.clear_invalid(self.ref_flags)
		return self.ref_flags


	@property
	def serialize(self):
		return {
			'ref_uuid'		: self.ref_uuid,
			'ref_business'	: self.ref_business,
			'ref_project'	: self.ref_project,
			'ref_content'	: self.ref_content
			#'ref_flags'		: "0x%08X" % self.ref_flags
		}


	@staticmethod
	def get_by_refid(ref_id):
		referral = session.get('referrals', {}).get(ref_id, None)
		try:
			if (referral and referral.ref_uuid): return referral
		except DetachedInstanceError as die:
			# committing / adding to db.session deletes instance;
			# thus we need to remove object reference in session
			del session['referrals'][ref_id]
		except Exception as e:
			print type(e), e

		try:
			referral = Referral.query.filter_by(ref_uuid=ref_id).one()
		except NoResultFound as nrf: pass
		return referral



	@staticmethod
	def get_composite_referral_by_id(ref_id):
		comp_ref = None
		try:
			business = aliased(Business, name='business')
			location = aliased(Location, name='location')
			comp_ref = database.session.query(Referral, business, location)	\
					.filter(Referral.ref_uuid == ref_id)	\
					.join(business,	     Referral.ref_business == business.bus_id)	\
					.outerjoin(location, Referral.ref_business == location.business)\
					.one()
			display_composite_referral(comp_ref)
		except NoResultFound as nrf:
			print type(nrf), nrf
		except Exception as e:
			print type(e), e
		return comp_ref



	@staticmethod
	def get_composite_referrals_by_profile(profile):
		""" get all referrals made by profile """
		business = aliased(Business, name='business')
		location = aliased(Location, name='location')
		comp_ref = database.session.query(Referral, business, location)	\
					.filter(Referral.ref_profile == profile.prof_id)	\
					.join(business, Referral.ref_business  == business.bus_id)	\
					.outerjoin(location, location.business == business.bus_id)	\
					.all()
		map(lambda composite: display_composite_referral(composite), comp_ref)
		return comp_ref



	@staticmethod
	def get_referrals_by_business(business):
		""" get all referrals made for business """
		profile	 = aliased(Profile, name='profile')
		compref = database.session.query(Referral, profile)	\
					.filter(Referral.ref_business == business.bus_id)	\
					.join(profile, Referral.ref_profile == profile.prof_id)	\
					.all()
		return compref



class RefList(database.Model):
	__tablename__ = "referral_list"
	list_uuid		= Column(String(40), primary_key=True, index=True)
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


	def add_referral(self, referral):
		# only do this at commit time.
		if (referral.invalid()): return	False #raise exception(Invalid Referral)
		if (self.contains_referral(referral)): return True# raise referral exists

		try:
			database.session.add(self)
			database.session.add(referral)

			mapping = RefListReferralMap(self, referral)
			database.session.add(mapping)
			database.session.commit()
			return True
		except Exception as e:
			print type (e), e
			database.session.rollback()
		return False


	def get_referral_ids(self):
		return RefListReferralMap.get_referral_ids(self)

	def get_referrals(self):
		referral_ids = self.get_referral_ids()
		# for each, get the obj
		return referral_ids


	def contains_referral(self, referral):
		try:
			print 'lets query for ', self.list_uuid, referral.ref_uuid
			reflist = RefListReferralMap.query.filter_by(map_reflist=self.list_uuid)	\
								 			  .filter_by(map_referal=referral.ref_uuid)	\
											  .all()
			print reflist
		except Exception as e:
			print type(e), e
		return reflist


	def profile_can_modify(self, profile):
		try:
			reflist = RefListMemberMap.query.filter_by(map_reflist=self.list_uuid)	\
											.filter_by(map_profile=profile.prof_id)	\
											.all()
		except Exception as e:
			print type(e), e
		return reflist

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
		try:
			if (reflist and reflist.list_uuid): return reflist
		except DetachedInstanceError as die:
			# committing / adding to db.session deletes instance;
			# thus we need to remove object reference in session
			del session['lists'][list_id]
		except Exception as e:
			print type(e), e

		try:
			reflist = RefList.query.filter_by(list_uuid=list_id).one()
		except NoResultFound as nrf: pass
		return reflist



class RefListMemberMap(database.Model):
	__tablename__ = "referral_list_member_map"

	id			= Column(Integer, primary_key=True, unique=True)
	map_reflist	= Column(String(40), ForeignKey('referral_list.list_uuid'), nullable=False, index=True)
	map_profile	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False)		# member
	map_control	= Column(Integer, default=0)											# member's ACL

	def __init__ (self, reflist, profile, control):
		self.map_reflist = reflist
		self.map_profile = profile
		self.map_control = control

	
	@staticmethod
	def profile_can_modify_list(profile, reflist):
		try:
			reflist = RefListMemberMap.query.filter_by(map_reflist=reflist.list_uuid)	\
											.filter_by(map_profile=profile.prof_id)	\
											.all()
		except Exception as e:
			print type(e), e
		return reflist





class RefListReferralMap(database.Model):
	__tablename__ = "referral_list_referral_map"

	id				= Column(Integer, primary_key=True, unique=True)
	map_reflist	= Column(String(40), ForeignKey('referral_list.list_uuid'), nullable=False, index=True)
	map_referal	= Column(String(40), ForeignKey('referral.ref_uuid'),       nullable=False, index=True)

	def __init__ (self, reflist, referral):
		#if (referral.invalid()): raise exception(Invalid Referral)
		self.map_reflist = reflist.list_uuid
		self.map_referal = referral.ref_uuid

	
	@staticmethod
	def get_referral_ids(reflist):
		return [ r.map_referal for r in RefListReferralMap.query.filter_by(map_reflist=reflist.list_uuid).all() ]




#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################

def display_composite_referral(composite):
	# COMPOSITE REFERRAL OBJECT
	# OBJ.Referral	# Referral
	# OBJ.business	# Business of Referral
	# OBJ.location	# Location of Business (maybe None)

	composite.display_city = None # 'No address listed'
	composite.display_addr = None # 'No address listed'

	if composite.location:
		composite.display_city = composite.location.display_city_state()
		composite.display_addr = composite.location.display_address()

