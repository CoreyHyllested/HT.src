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

		self.buyer = ProfileFactory.create()
		self.sellr = ProfileFactory.create()

		self.the_meeting = MeetingFactory.create(meet_buyer=self.buyer.prof_id, meet_sellr=self.sellr.prof_id)
		db_session.add(self.the_meeting)


	def tearDown(self):
		self.app_context.pop()


	def test_state_lookup_table(self):
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


	def test_proposed_state_defaults(self):
		# create a very standard meeting.
		meeting = MeetingFactory.create()
		self.assertTrue(meeting.proposed())
		self.assertTrue(meeting.meet_owner == meeting.meet_sellr)
		self.assertTrue(meeting.meet_tz == 'US/Pacific')

	def test_meeting_init_without_card(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(meet_card=None))
	def test_meeting_init_without_cust(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(customer=None))
	def test_meeting_init_without_token(self): self.assertRaises(SanitizedException, lambda: MeetingFactory.create(meet_token=None))


	def test_meeting_get_by_id(self):
		new_meeting = MeetingFactory.create()
		db_session.add(new_meeting)

		meeting = Meeting.get_by_id(new_meeting.meet_id)
		self.assertEqual(meeting, new_meeting)

		meeting = Meeting.get_by_id(None)
		self.assertEqual(meeting, None)

		meeting = Meeting.get_by_id('an-valid-id')
		self.assertEqual(meeting, None)


	def test_transition_PROPOSED_to_ACCEPTED(self):
		print self.the_meeting.meet_sellr
		self.the_meeting.set_state(MeetingState.ACCEPTED, self.sellr)
		self.assertEqual(self.the_meeting.meet_state, MeetingState.ACCEPTED)




#	def test_get_duration_in_hours(self):
#		new_meeting = MeetingFactory.create()
#		print new_meeting.get_duration_in_hours()

