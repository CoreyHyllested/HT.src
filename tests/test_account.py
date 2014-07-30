import unittest

from flask import current_app
from flask import render_template, make_response, session, request, redirect, url_for
from server import  initialize_server
from server.models import *


class TestAccount(unittest.TestCase):
	def setUp(self):
		self.app = initialize_server('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		self.app_context.pop()


	def test_bad_name_for_account(self):
		bad_account = Account.get_by_uid('no_account')
		self.assertTrue(bad_account == None)


	def test_create_factory_boy_accounts(self):
		acct = AccountFactory.create()
		print acct.userid
		print acct.name
		print acct.email

		self.assertTrue(acct.name == 'Test User 1')
		self.assertTrue(acct.email == 'corey+TestUser1@insprite.co')
		self.assertTrue(acct.pwhash	== 'pwtest')


