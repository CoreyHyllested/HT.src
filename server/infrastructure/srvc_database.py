#################################################################################
# Copyright (C) 2013 - 2014 HeroTime, Inc.
# All Rights Reserved.
# 
# All information contained is the property of HeroTime, Inc.  Any intellectual 
# property about the design, implementation, processes, and interactions with 
# services may be protected by U.S. and Foreign Patents.  All intellectual 
# property contained within is covered by trade secret and copyright law.   
# 
# Dissemination or reproduction is strictly forbidden unless prior written 
# consent has been obtained from HeroTime, Inc.
#################################################################################


import os
from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = 'postgresql://htdb:passw0rd@beta1.cesf5wqzwzr9.us-east-1.rds.amazonaws.com:5432/htdb'
SQLALCHEMY_MIGRATE_REPO = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db_repository')

# to make this work in ht_server ... add this code to ht_server app context somewhere (__init__?)
# gotten from http://flask.pocoo.org/docs/patterns/sqlalchemy/ ... under Declaritive

#from yourapplication.database import db_session
#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    db_session.remove()

print 'import::db -- create engine'
#engine = create_engine('postgresql://htdb:passw0rd@htdb.cesf5wqzwzr9.us-east-1.rds.amazonaws.com:5432/htdb', echo=True)
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

print 'import::db -- create sessionmaker'
db_session = scoped_session(sessionmaker(bind=engine))

print 'import::db -- create db base'
Base = declarative_base()
Base.query = db_session.query_property()


# models uses (Base)
from server.infrastructure.models import *

def init_db():
	# configure postgresql, by creating
	print 'import::db -- create_all()'
	Base.metadata.create_all(bind=engine)
	print 'returned'
