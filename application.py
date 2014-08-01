#!/usr/bin/env python
import os, sys
from server import  initialize_server
from config import	server_configuration
from flask.ext.script import Manager, Shell
from OpenSSL import SSL


ENV_CONFIG	= os.getenv('INSPRITE_CONFIG')
if (ENV_CONFIG == 'devel_money'):
	print "\n\n\n\nI too like to live dangerously.\n Serious.\nYou're entering the DangerZone"
application = initialize_server(ENV_CONFIG or 'default')
manager = Manager(application)


def run_manager():
	def mk_insprite_shell_ctx():
		return dict(app=application)
	manager.add_command("shell", Shell(make_context=mk_insprite_shell_ctx))
	manager.run()


def main():
	# print 'Run with SSH'
	context = SSL.Context(SSL.SSLv23_METHOD)
	context.use_privatekey_file('security/herotime-pk.pem')
	context.use_certificate_file('security/herotime.crt')
	application.run(debug = True, ssl_context=context)

@manager.command
def test():
	"""Run unit tests"""
	if (ENV_CONFIG != 'testing'): raise Exception('\nFailure: Running with incorrect CONFIG(' + str(ENV_CONFIG) + ') rerun as:\nINSPRITE_CONFIG=testing python ./application.py test')
	import unittest
	all_tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(all_tests)



if __name__ == "__main__":
	if (len(sys.argv) >= 2):
		run_manager()
	else:
		main()
