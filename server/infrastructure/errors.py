import sys


#IndexError: list index out of range
#seen: we tried to index a list (from DB) that was zero



class InvalidCreditCard(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
