from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref
from datetime import datetime as dt
import datetime
import uuid


ROLE_USER = 1

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True)
    nickname = Column(String(64), index = True, unique = True)
    email = Column(String(120), index = True, unique = True)
    role = Column(Integer, default = ROLE_USER)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(Base):
	__tablename__ = "post"
	id = Column(Integer, primary_key = True)
	body = Column(String(140))
	timestamp = Column(DateTime)
	user_id = Column(Integer, ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)
