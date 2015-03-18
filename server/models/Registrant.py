#################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
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



# Flags and States for Registered Users (Preview Site)
REG_FLAG_ROLE_NONE = 0
REG_FLAG_ROLE_LEARN = 1
REG_FLAG_ROLE_TEACH = 2
REG_FLAG_ROLE_BOTH = 3

REG_STATE_ROLE_NONE = (0x1 << REG_FLAG_ROLE_NONE)
REG_STATE_ROLE_LEARN = (0x1 << REG_FLAG_ROLE_LEARN)
REG_STATE_ROLE_TEACH = (0x1 << REG_FLAG_ROLE_TEACH)
REG_STATE_ROLE_BOTH = (0x1 << REG_FLAG_ROLE_BOTH)

def set_flag(state, flag):  return (state | (0x1 << flag))
def test_flag(state, flag): return (state & (0x1 << flag))


class Registrant(Base):
	"""Account for interested parties signing up through the preview.insprite.co."""
	__tablename__ = "registrant"

	reg_userid  = Column(String(40), primary_key=True, index=True, unique=True)
	reg_email   = Column(String(128), index=True, unique=True)
	reg_location = Column(String(128))
	reg_ip = Column(String(20))
	reg_name    = Column(String(128))
	reg_org    = Column(String(128))	
	reg_referrer = Column(String(128))
	reg_flags = Column(Integer, default=0)
	reg_created = Column(DateTime())
	reg_updated = Column(DateTime())
	reg_comment = Column(String(1024))
	reg_referral_code = Column(String(128))

	def __init__ (self, reg_email, reg_location, reg_ip, reg_org, reg_referrer, reg_flags, reg_comment, reg_referral_code):
		self.reg_userid = str(uuid.uuid4())
		self.reg_email  = reg_email
		self.reg_location  = reg_location
		self.reg_ip  = reg_ip
		self.reg_org  = reg_org
		self.reg_referrer  = reg_referrer
		self.reg_flags  = reg_flags
		self.reg_comment = reg_comment
		self.reg_created = dt.utcnow()
		self.reg_updated = dt.utcnow()
		self.reg_referral_code  = reg_referral_code

	def __repr___ (self):
		return '<Registrant %r, %r, %r, %r>'% (self.reg_userid, self.reg_email, self.reg_location, self.reg_flags)


	@staticmethod
	def get_by_regid(regid):
		registrants = Registrant.query.filter_by(reg_userid=regid).all()
		if len(registrants) != 1: raise NoAccountFound(regid, 'Sorry, no account found')
		return registrants[0]



################################################################################
#### EXAMPLE: Reading from PostgreSQL. #########################################
################################################################################
# psql "dbname=d673en78hg143l host=ec2-54-235-70-146.compute-1.amazonaws.com user=ezjlivdbtrqwgx password=lM5sTTQ8mMRM7CPM0JrSb50vDJ port=5432 sslmode=require"
# psql postgresql://name:password@instance:port/database
################################################################################


################################################################################
#### EXAMPLE: DELETING A ROW from PostgreSQL. ##################################
################################################################################
# delete from timeslot where location = 'San Francisco';
# delete from timeslot where id >= 25;
# delete from review where heroid = '559a73f1-483c-40fe-8ee5-83118ce1f7e3';

################################################################################
#### EXAMPLE: ALTER TABLE from PostgreSQL. #####################################
################################################################################
# BEGIN; 
# LOCK appointments;
# ALTER TABLE appointments ADD   COLUMN challenge   varchar(40); 
# ALTER TABLE appointments ALTER COLUMN transaction drop not null; 
# END; 
################################################################################
# BEGIN; 
# UPDATE appointment2 SET buyer_prof = 62e9e608-12cd-4b47-9eb4-ff6998dca89a WHERE 
################################################################################

################################################################################
#### EXAMPLE: INSERT ROW INTO TABLE from PostgreSQL. ###########################
################################################################################
# begin;
# insert into umsg (msg_id, msg_to, msg_from, msg_thread, msg_content, msg_created) VALUES ('testing-1-2-3-4-5', (select prof_id from profile where prof_name like '%Corey%'), (select prof_id from profile where prof_name like '%Frank%'), 'testing-1-2-3-4-5', 'Garbage in, garbage out', '2014-06-05 17:59:12.311562');
# commit;
################################################################################
 
################################################################################
#### EXAMPLE: FIND ALL DUPLICATE VALUES IN COLUMN. #############################
################################################################################
# begin;
# select count(msg_thread), msg_thread from umsg group by msg_thread having count(msg_thread) > 1;
# commit;
#### RESULTS ###################################################################
#  count |              msg_thread
# -------+--------------------------------------
#     3 | 1dfb5322-69c0-4a58-a768-ee66bcd1b9c6
#     2 | 45eb702c-1e4c-4971-94dc-44b267930854
#     5 | fd6d1310-809a-41bc-894a-da75b21aa315

