import unittest

from flask import current_app
from flask import render_template, make_response, session, request, redirect, url_for
from server import  initialize_server
from server.models import *

class MeetingTestCase(unittest.TestCase):
	def setUp(self):
		self.app = initialize_server('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		self.app_context.pop()

	
	def test_lookup_table(self):
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[0] == 'PROPOSED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[1] == 'ACCEPTED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[2] == 'CHARGE CREDIT CARD')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[3] == 'OCCURRED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[4] == 'COMPLETE')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[5] == 'RESOLVED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[10] == 'REJECTED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[11] == 'TIMEDOUT')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[20] == 'CANCELED')
		self.assertTrue(MeetingState.MEETING_STATE_LOOKUP_TABLE[30] == 'DISPUTED')

