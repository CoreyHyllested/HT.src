import unittest

from flask import current_app
from flask import render_template, make_response, session, request, redirect, url_for
from server import  initialize_server
from server.infrastructure.errors import *
from server.models import *

class MeetingTestCase(unittest.TestCase):
	def setUp(self):

		self.app = initialize_server('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client(use_cookies=True)

		self.buyer_acct = AccountFactory.create()
		self.sellr_acct = AccountFactory.create()

		self.buyer = ProfileFactory.create(prof_acct=self.buyer_acct.userid)
		self.sellr = ProfileFactory.create(prof_acct=self.sellr_acct.userid)
		self.oauth = OauthFactory.create(ht_account=self.sellr_acct.userid)
#		print
#		print self.sellr_acct.userid
#		print self.sellr.account
#		print self.oauth.ht_account

		meetings = MeetingFactory.create_batch(5, meet_buyer=self.buyer.prof_id, meet_sellr=self.sellr.prof_id)
		self.meeting_proposed = meetings[0]
		self.meeting_accepted = meetings[1]
		self.meeting_chargecc = meetings[2]
		self.meeting_occurred = meetings[3]
		self.meeting_complete = meetings[4]

		self.meeting_accepted.meet_state = MeetingState.ACCEPTED
		self.meeting_chargecc.meet_state = MeetingState.CHARGECC
		self.meeting_occurred.meet_state = MeetingState.OCCURRED
		self.meeting_complete.meet_state = MeetingState.COMPLETE

		db_session.add(self.meeting_proposed)
		db_session.add(self.meeting_accepted)
		db_session.add(self.meeting_chargecc)
		db_session.add(self.meeting_occurred)
		db_session.add(self.meeting_complete)
		db_session.add(self.buyer)
		db_session.add(self.sellr)
		db_session.add(self.buyer_acct)
		db_session.add(self.sellr_acct)
		db_session.add(self.oauth)


	def tearDown(self):
		self.app_context.pop()


	def est_state_lookup_table(self):
		self.assertTrue(MeetingState.state_name(MeetingState.PROPOSED) == 'PROPOSED')
		self.assertTrue(MeetingState.state_name(MeetingState.ACCEPTED) == 'ACCEPTED')
		self.assertTrue(MeetingState.state_name(MeetingState.CHARGECC) == 'CHARGE CREDIT CARD')
		self.assertTrue(MeetingState.state_name(MeetingState.OCCURRED) == 'OCCURRED')
		self.assertTrue(MeetingState.state_name(MeetingState.COMPLETE) == 'COMPLETE')
		self.assertTrue(MeetingState.state_name(MeetingState.RESOLVED) == 'RESOLVED')
		self.assertTrue(MeetingState.state_name(MeetingState.REJECTED) == 'REJECTED')
		self.assertTrue(MeetingState.state_name(MeetingState.TIMEDOUT) == 'TIMEDOUT')
		self.assertTrue(MeetingState.state_name(MeetingState.CANCELED) == 'CANCELED')
		self.assertTrue(MeetingState.state_name(MeetingState.DISPUTED) == 'DISPUTED')


	def est_proposed_state_defaults(self):
		# create a very standard meeting.
		meeting = MeetingFactory.create()
		self.assertTrue(meeting.proposed())
		self.assertTrue(meeting.meet_owner == meeting.meet_sellr)
		self.assertTrue(meeting.meet_tz == 'US/Pacific')

	def est_meeting_init_without_card(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(meet_card=None))
	def est_meeting_init_without_cust(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(customer=None))
	def est_meeting_init_without_token(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(meet_token=None))


	def est_meeting_get_by_id(self):
		meeting = Meeting.get_by_id(self.meeting_proposed.meet_id)
		self.assertEqual(meeting.meet_id, self.meeting_proposed.meet_id)

		meeting = Meeting.get_by_id(None)
		self.assertEqual(meeting, None)

		meeting = Meeting.get_by_id('an-valid-id')
		self.assertEqual(meeting, None)


	def est_transition_PROPOSED_to_ACCEPTED(self):
		self.meeting_proposed.set_state(MeetingState.ACCEPTED, self.sellr)
		self.assertEqual(self.meeting_proposed.meet_state, MeetingState.ACCEPTED)

	def est_transition_PROPOSED_to_REJECTED(self):
		self.meeting_proposed.set_state(MeetingState.REJECTED, self.sellr)
		self.assertEqual(self.meeting_proposed.meet_state, MeetingState.REJECTED)

	def est_transition_PROPOSED_to_TIMEDOUT(self):
		self.meeting_proposed.set_state(MeetingState.TIMEDOUT, self.sellr)
		self.assertEqual(self.meeting_proposed.meet_state, MeetingState.TIMEDOUT)
	
	def test_transition_ACCEPTED_to_CHARGECC(self):
		self.meeting_accepted.set_state(MeetingState.CHARGECC, self.sellr)
		self.assertEqual(self.meeting_accepted.meet_state, MeetingState.CHARGECC)

	def est_transition_ACCEPTED_to_CANCELED(self):
		self.meeting_accepted.set_state(MeetingState.CANCELED, self.sellr)
		self.assertEqual(self.meeting_accepted.meet_state, MeetingState.CANCELED)

	def est_transition_PROPOSED_to_OTHERS(self):
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.PROPOSED))

		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.CHARGECC))
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.OCCURRED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.COMPLETE))
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.DISPUTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.RESOLVED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_proposed.set_state(MeetingState.CANCELED))




	def est_transition_ACCEPTED_to_OTHERS(self):
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.ACCEPTED))

		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.PROPOSED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.REJECTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.TIMEDOUT))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.OCCURRED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.COMPLETE))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.DISPUTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_accepted.set_state(MeetingState.RESOLVED))



	def est_transition_CHARGECC_to_OTHERS(self):
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.CHARGECC))

		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.PROPOSED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.REJECTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.TIMEDOUT))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.ACCEPTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.COMPLETE))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.DISPUTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_chargecc.set_state(MeetingState.RESOLVED))



	def est_transition_OCCURRED_to_OTHERS(self):
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.OCCURRED))

		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.PROPOSED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.REJECTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.TIMEDOUT))
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.ACCEPTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.CHARGECC))
		self.assertRaises(StateTransitionError, lambda: self.meeting_occurred.set_state(MeetingState.RESOLVED))


	def est_transition_COMPLETE_to_OTHERS(self):
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.COMPLETE))

		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.PROPOSED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.REJECTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.TIMEDOUT))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.ACCEPTED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.CHARGECC))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.OCCURRED))
		self.assertRaises(StateTransitionError, lambda: self.meeting_complete.set_state(MeetingState.RESOLVED))
"""
"""

#									MeetingState.CHARGECC	: { MeetingState.OCCURRED	: __transition_chargecc_to_occurred,
#																MeetingState.CANCELED	: __transition_chargecc_to_canceled, },
#									MeetingState.OCCURRED	: { MeetingState.COMPLETE	: __transition_occurred_to_complete,
#									MeetingState.CHARGECC	: { MeetingState.OCCURRED	: __transition_chargecc_to_occurred,
#																MeetingState.CANCELED	: __transition_chargecc_to_canceled, },
#									MeetingState.OCCURRED	: { MeetingState.COMPLETE	: __transition_occurred_to_complete,
#																MeetingState.DISPUTED	: __transition_occurred_to_disputed, },
#									MeetingState.COMPLETE	: { MeetingState.DISPUTED	: __transition_complete_to_disputed, },
#									MeetingState.DISPUTED	: { MeetingState.DISPUTED	: __transition_disputed_to_resolved, },


#	def test_get_duration_in_hours(self):
#		new_meeting = MeetingFactory.create()
#		print new_meeting.get_duration_in_hours()

