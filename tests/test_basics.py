import unittest
from flask import current_app
from server import  initialize_server


class BasicTestCase(unittest.TestCase):
	def setUp(self):
		self.app = initialize_server('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()

	def tearDown(self):
		self.app_context.pop()

	def test_app_exists(self):
		self.assertFalse(current_app is None)
	
	def test_app_is_testing(self):
		print current_app.config['TESTING']
		self.assertTrue(current_app.config['TESTING'])
