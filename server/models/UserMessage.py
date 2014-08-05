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



MSG_FLAG_LASTMSG_READ = 0
MSG_FLAG_SEND_ARCHIVE = 1		#The original-message sender archived thread
MSG_FLAG_RECV_ARCHIVE = 2		#The original-message receiver archived thread
MSG_FLAG_THRD_UPDATED = 3		#A message was responded too.

MSG_STATE_LASTMSG_READ	= (0x1 << MSG_FLAG_LASTMSG_READ)	#1
MSG_STATE_SEND_ARCHIVE	= (0x1 << MSG_FLAG_SEND_ARCHIVE)	#2
MSG_STATE_RECV_ARCHIVE	= (0x1 << MSG_FLAG_RECV_ARCHIVE)	#4
MSG_STATE_THRD_UPDATED	= (0x1 << MSG_FLAG_THRD_UPDATED)	#8



class UserMessage(Base):
	__tablename__ = "umsg"
	msg_id		= Column(String(40), primary_key=True, unique=True)													# NonSequential ID
	msg_to		= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	msg_from	= Column(String(40), ForeignKey('profile.prof_id'), nullable=False, index=True)
	msg_thread	= Column(String(40), nullable=False, index=True)
	msg_parent  = Column(String(40))
	msg_content = Column(String(1024), nullable=False)
	msg_created = Column(DateTime(), nullable=False)
	msg_noticed = Column(DateTime())
	msg_opened  = Column(DateTime())
	msg_subject	= Column(String(64))
	msg_flags	= Column(Integer, default=0)


	def __init__ (self, prof_to, prof_from, content, subject=None, thread=None, parent=None):
		self.msg_id	= str(uuid.uuid4())
		self.msg_to	= str(prof_to)
		self.msg_from = str(prof_from)
		self.msg_content = str(content)
		self.msg_subject = subject
		self.msg_created = dt.utcnow()

		if (thread == None):
			# First message in thread
			thread = str(self.msg_id)
			parent = None
			if (self.msg_subject is None): raise Exception('first msg needs subject')
		else:
			# thread is not None, parent must exist; set flags properly
			if (parent == None): raise Exception('not valid threading')	
			self.msg_flags = MSG_STATE_THRD_UPDATED

		self.msg_thread	= thread
		self.msg_parent	= parent

	def __repr__(self):
		content = self.msg_content[:20]
		subject = self.msg_subject[:15]
		ts_open = self.msg_opened.strftime('%b %d %I:%M') if self.msg_opened is not None else str('Unopened')
		return '<umsg %r|%r\t%r\t%r\t%r\t%r\t%r>' % (self.msg_id, self.msg_thread, self.msg_parent, self.msg_flags, ts_open, self.msg_from, subject)


	@staticmethod
	def get_by_msg_id(uid):
		msgs = UserMessage.query.filter_by(msg_id=uid).all()
		if len(msgs) != 1: raise NoResourceFound('UserMessage', uid)
		return msgs[0]


	@property
	def serialize(self):
		return {
			'msg_id'		: str(self.msg_id),
			'msg_to'		: self.msg_to,
			'msg_from'		: self.msg_from,
			'msg_flags'		: self.msg_flags,
			'msg_subject'	: str(self.msg_subject),
			'msg_content'	: str(self.msg_content),
			'msg_parent'	: str(self.msg_parent),
			'msg_thread'	: str(self.msg_thread),
		}


	def archived(self, profile_id):
		if (profile_id == self.msg_to):		return (self.msg_flags & MSG_STATE_RECV_ARCHIVE)
		if (profile_id == self.msg_from):	return (self.msg_flags & MSG_STATE_SEND_ARCHIVE)
		raise Exception('profile_id(%s) does not match msg(%s) TO or FROM' % (profile_id, self.msg_id))
		


