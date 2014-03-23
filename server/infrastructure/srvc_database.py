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


from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


# to make this work in ht_server ... add this code to ht_server app context somewhere (__init__?)
# gotten from http://flask.pocoo.org/docs/patterns/sqlalchemy/ ... under Declaritive

#from yourapplication.database import db_session
#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    db_session.remove()

print 'import::db -- create engine'
engine = create_engine('postgresql://wvqtppohnrryzx:2BJAtMLHVVYjP9C5ueBdV4J33a@ec2-50-19-219-235.compute-1.amazonaws.com:5432/d21dfk3trnunjm')

print 'import::db -- create sessionmaker'
db_session = scoped_session(sessionmaker(bind=engine))

print 'import::db -- create db base'
Base = declarative_base()
Base.query = db_session.query_property()


# must come after Base
from server.infrastructure.models import *

def init_db():
	# configure postgresql, by creating
	print 'import::db -- create_all()'
	Base.metadata.create_all(bind=engine)
	db_session.commit()
	print 'returned'



#print 'import -- create sq SM'
#sq = SM()

# must do this (approx.) last.
#print sq.query(models.Review).join(models.Profile, models.Review.author == models.Profile.id).all()
