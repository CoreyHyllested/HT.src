import unittest

from flask import current_app
from flask import render_template, make_response, session, request, redirect, url_for
from server import  initialize_server


class BasicTestCase(unittest.TestCase):
	def setUp(self):
		self.app = initialize_server('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		self.app_context.pop()

	def test_app_exists(self):
		self.assertFalse(current_app is None)
	
	def test_app_is_testing(self):
		self.assertTrue(current_app.config['TESTING'])

	def test_landing_page(self):
		resp = self.client.get(url_for('insprite.render_landingpage'))
		self.assertTrue('NEED A HAND' in resp.get_data(as_text=True))

	def test_login_with_wrong_password(self):
		resp = self.client.post(url_for('insprite.render_login'), data = {
			'input_login_email'		: 'corey@insprite.co',
			'input_login_password'	: 'NOT_THE_CORRECT_PASSWORD',
		})
		print resp
		self.assertTrue(resp.status_code == 400)


	def test_login_with_correct_password(self):
		resp = self.client.post(url_for('insprite.render_login'), data = {
			'input_login_email'		: 'corey@insprite.co',
			'input_login_password'	: 'passw0rd',
		})
		print resp
		self.assertTrue(resp.status_code == 200)
