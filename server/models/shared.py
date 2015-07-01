#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents. All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################


################################################################################
### EMAIL POLICY FIELD #########################################################
################################################################################
################################################################################
## 	BIT-RANGE		NAME			DETAILS
################################################################################
## 	0 - 4			Receipts			Receipts for action taken.
##	8 				USERMSG_RECVD		Notification that user sent a message.
##  9				REVIEW_POSTED		Notificaiton that a user reviewed you.
##  16				Meeting Reminder	Reminder sent 24 hours before.
################################################################################
##  4-15,18,19,21-31				reserved
################################################################################

class EmailPolicy:
	# Receipts for actions I take
	EMAIL_BIT_RECPT_ACCEPT = 0
	EMAIL_BIT_RECPT_REJECT = 1
	EMAIL_BIT_RECPT_CANCEL = 2
	EMAIL_BIT_RECPT_REVIEW = 3
	EMAIL_BIT_RECPT_MESSGE = 4

	# Non-Critical Messages to a user.
	EMAIL_BIT_USERMSG_RECVD = 8
	EMAIL_BIT_REVIEW_POSTED = 9

	# Reminder emails.
	EMAIL_BIT_REMIND_MEETING = 16
	EMAIL_BIT_REMIND_REVIEWS = 17

	# Receipts for actions I take
	EMAIL_POLICY_RECPT_ACCEPT = (0x1 << EMAIL_BIT_RECPT_ACCEPT)
	EMAIL_POLICY_RECPT_REJECT = (0x1 << EMAIL_BIT_RECPT_REJECT)
	EMAIL_POLICY_RECPT_CANCEL = (0x1 << EMAIL_BIT_RECPT_CANCEL)
	EMAIL_POLICY_RECPT_REVIEW = (0x1 << EMAIL_BIT_RECPT_REVIEW)
	EMAIL_POLICY_RECPT_MESSGE = (0x1 << EMAIL_BIT_RECPT_MESSGE)
	EMAIL_POLICY_RECEIPTS = EMAIL_POLICY_RECPT_ACCEPT | EMAIL_POLICY_RECPT_REJECT | EMAIL_POLICY_RECPT_CANCEL | EMAIL_POLICY_RECPT_REVIEW | EMAIL_POLICY_RECPT_MESSGE

	# Non-Critical Messages to a user.
	EMAIL_POLICY_USERMSG_RECVD	= (0x1 << EMAIL_BIT_USERMSG_RECVD)
	EMAIL_POLICY_REVIEW_POSTED	= (0x1 << EMAIL_BIT_REVIEW_POSTED)
	EMAIL_POLICY_REMIND_MEETING = (0x1 << EMAIL_BIT_REMIND_MEETING)
	EMAIL_POLICY_REMIND_REVIEWS = (0x1 << EMAIL_BIT_REMIND_REVIEWS)




################################################################################
### AccountRole	################################################################
################################################################################

class AccountRole:
	CUSTOMER		= 0
	CRAFTSPERSON	= 16
	ADMIN			= 1024

	LOOKUP_TABLE = {
		CUSTOMER		: 'CUSTOMER',
		CRAFTSPERSON	: 'CRAFTSPERSON',
		ADMIN			: 'ADMIN',
	}

	@staticmethod
	def name(state):
		return AccountRole.LOOKUP_TABLE.get(state, 'UNDEFINED')




################################################################################
### OauthProvider ##############################################################
################################################################################

class OauthProvider:
	NONE   = 0
	LINKED = 1
	STRIPE = 2
	GOOGLE = 3
	FACEBK = 4
	TWITTR = 5


