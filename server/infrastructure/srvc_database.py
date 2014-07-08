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


from server import ht_server
from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URI = ht_server.config['SQLALCHEMY_DATABASE_URI']
MIGRATE_REPO = ht_server.config['SQLALCHEMY_MIGRATE_REPO']

# to make this work in ht_server ... add this code to ht_server app context somewhere (__init__?)
# gotten from http://flask.pocoo.org/docs/patterns/sqlalchemy/ ... under Declaritive

#from yourapplication.database import db_session
#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    db_session.remove()

#print 'init::db -- create engine and scoped connection'
db_engine	= create_engine(DATABASE_URI) #, echo=True)
db_session	= scoped_session(sessionmaker(bind=db_engine))

Base = declarative_base(bind=db_engine)
Base.query = db_session.query_property()


# models uses (Base)
from server.infrastructure import models
