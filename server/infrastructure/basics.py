from datetime import datetime as dt, timedelta
from pprint import pprint as pp
from server.infrastructure.errors import *
from server.infrastructure.models import *
import json, smtplib



#def ht_sanitize_errors(e, details=None):
#	msg = 'caught error:' + str(e)
#	return msg

def get_account_and_profile(profile_id):
	try:
		p = Profile.get_by_prof_id(profile_id)
		a = Account.get_by_uid(p.account)
	except Exception as e:
		print "Oh shit, caught error at get_account_and_profile" + e
		raise e
	return (a, p)


def get_proposal_email_info(proposal):
	(ha, hp) = get_account_and_profile(proposal.prop_hero)
	(ba, bp) = get_account_and_profile(proposal.prop_user)

	hero_addr = ha.email
	user_addr = ba.email
	hero_name = hp.prof_name.encode('utf8', 'ignore')
	user_name = bp.prof_name.encode('utf8', 'ignore')
	return (hero_addr, hero_name, user_addr, user_name)
