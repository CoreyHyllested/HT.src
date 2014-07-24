from datetime import datetime as dt, timedelta
from pprint import pprint as pp
from server.infrastructure.errors import *
from server.infrastructure.models import *
import json, smtplib



def get_account_and_profile(profile_id):
	try:
		p = Profile.get_by_prof_id(profile_id)
		a = Account.get_by_uid(p.account)
	except Exception as e:
		print "Oh shit, caught error at get_account_and_profile" + e
		raise e
	return (a, p)

