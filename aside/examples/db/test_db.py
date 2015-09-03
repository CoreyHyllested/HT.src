#!/usr/bin/env python

from sqlalchemy import *     #create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

#from sqlalchemy.orm import sessionmaker
#from os import environ



################################################################################
#### EXAMPLE: Creating a new URI resource. #####################################
################################################################################
# @app.route("/create", methods=['PUT', 'POST'])
# def create(): CODE.
################################################################################


################################################################################
#### EXAMPLE: Reading from the DB. #############################################
################################################################################
# psql -h ec2-54-221-224-138.compute-1.amazonaws.com -p 5432 -U pzjceewfijwnfl ddpft5o6pfgl4n
# HOST: ec2-54-221-224-138.compute-1.amazonaws.com
# PORT: 5432
# USER: pzjceewfijwnfl
# DBSE: ddpft5o6pfgl4n   (may be multiple db per server, we have multiple tables
# PASS: 
# ngin = create_engine('postgresql://pzjceewfijwnfl:1yF5F3qglIr8_IHi-xfMmLZorl@ec2-54-221-224-138.compute-1.amazonaws.com')
#ngin= create_engine('postgresql://pzjceewfijwnfl:1yF5F3qglIr8_IHi-xfMmLZorl@ec2-54-221-224-138.compute-1.amazonaws.com/ddpft5o6pfgl4n')   
################################################################################


db_base = declarative_base()

class verifyEmail(db_base):
	__tablename__ = 'verifyEmail'
	regNr  = Column(Integer(), Sequence('ahero_seq',  start=1,  increment=1), primary_key=True)
	name   = Column(String(80))
	email  = Column(String(80))
	uniqId = Column(String(80))

	def __init__(self, name, email, uniqId):
		self.name   = name
		self.email  = email
		self.uniqId = uniqId

	


class ahero(db_base):
	__tablename__ = 'ahero'
	uid   = Column(Integer(), Sequence('ahero_seq',  start=1,  increment=1), primary_key=True)
	name  = Column(String(80))
	email = Column(String(80), unique=True)
	#type= Column(String())
	#__mapper_args__ = {'polymorphic_on': type}
	__table_args__ = {'implicit_returning':False}
	def __init__(self, name, email):
		self.name  = name
		self.email = email


db = create_engine('postgresql://pzjceewfijwnfl:1yF5F3qglIr8_IHi-xfMmLZorl@ec2-54-221-224-138.compute-1.amazonaws.com:5432/ddpft5o6pfgl4n', echo=True)   
db_base.metadata.create_all(db)	#import all info from db

user = ahero('Corey Hyllested', 'corey@herotime.co')
s = Session(db)
s.add(user)
s.commit()
s.close()


#also..
db.execute('CREATE TABLE hero(uid integer PRIMARY KEY, name varchar(80), email varchar(80) UNIQUE);')


def main():
	print 'hellow world'

if __name__ == "__main__":
    main()

