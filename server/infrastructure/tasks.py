from __future__ import absolute_import
from datetime import datetime as dt
from server.infrastructure.srvc_events	 import mngr
from server.infrastructure.srvc_database import db_session
from server.infrastructure.models		 import Account, Profile
from pprint import pprint as pp
import json


@mngr.task
def getDBCorey(x):
	print ('in getDBCorey' + str(x))
	accounts = Account.query.filter_by(email=('corey.hyllested@gmail.com')).all()
	print ('accounts = ' + str(len(accounts)))
	if (len(accounts) == 1):
		print str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)
	print 'exit getDBCorey'
	return str(accounts[0].userid) + ' ' + str(accounts[0].name) + ' ' + str(accounts[0].email)


@mngr.task
def add(x, y):
	return x+y 

@mngr.task
def xsum(numbers):
	return sum(numbers)


@mngr.task
def getTS(jsonObj):
	pp(jsonObj)
	return str(dt.now())

@mngr.task
def chargeStripe(jsonObj):
	print 'inside chargeStripe()'
	return None

@mngr.task
def enable_reviews(jsonObj):
	#is this submitted after stripe?  
	print 'enable_reviews()'
	return None

@mngr.task
def disable_reviews(jsonObj):
	#30 days after enable, shut it down!
	print 'disable_reviews()'
	return None
	

if __name__ != "__main__":
	print 'CAH: load server.tasks for @mngr.task'
else:
	print "Whoa, this is main"
