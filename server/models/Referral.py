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


from __future__ import absolute_import
from server.infrastructure.srvc_database import Base, db_session
from server.infrastructure.errors	import *
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt, timedelta
from pytz import timezone
import datetime, uuid



class Referral(Base):
	__tablename__ = "referral"

	ref_id = Column(String(40), primary_key=True, index=True, unique=True)
	ref_account = Column(String(40), ForeignKey('account.userid'), nullable=False, index=True)
	ref_shareid = Column(String(40), unique=True)
	ref_gift_id = Column(String(40))
	# ref_address = Column(String(64), nullable=False)  make this an email addres
	ref_created = Column(DateTime(), nullable=False)

	def __init__ (self, account, personalized=None, gift_id=None):
		self.ref_id = str(uuid.uuid4())
		self.ref_account = account
		self.ref_shareid = personalized
		self.ref_created = dt.utcnow()

		self.ref_gift_id = gift_id
		if (gift_id == 'CREATE'):
			print 'I should create the gift'
			pass

	def __repr__ (self):
		return '<Referral %r, %r>'% (self.ref_id, self.ref_account)


	@staticmethod
	def get_by_refid(ref):
		referral = None
		try: referral = Referral.query.filter_by(ref_id=ref).one()
		except NoResultFound as nrf: pass
		return referral


#TODO 
#get_by_refid: Raise Error NoReferralFound

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

