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


from datetime import datetime as dt, timedelta
from server.infrastructure.models		 import *
from server.infrastructure.errors		 import *
from pprint import pprint as pp
import json, smtplib



def get_account_and_profile(profile_id):
	try:
		p = Profile.get_by_prof_id(profile_id)
		a = Account.get_by_uid(p.account)
	except Exception as e:
		print type(e), e
		raise e
	return (a, p)




