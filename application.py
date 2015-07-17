#!/usr/bin/env python
import os, sys
from server import  initialize_server
from config import	server_configuration
from flask.ext.script	import Manager, Shell
from flask.ext.migrate	import Migrate, MigrateCommand
from OpenSSL import SSL


ENV_CONFIG	= os.getenv('INSPRITE_CONFIG')
if (ENV_CONFIG == 'devel_money'):
	print "\n\n\n\nI too like to live dangerously.\n Serious.\nYou're entering the DangerZone"

# used by shell
def make_shell_ctx():
	# access state with app.attr
	return dict(app=application)


application = initialize_server(ENV_CONFIG or 'default')
migrate	= Migrate(application, application.database)
manager = Manager(application)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_ctx))


@manager.command
def runserver():
	# print 'Run with SSH'
	context = SSL.Context(SSL.SSLv23_METHOD)
	context.use_privatekey_file('security/soulcrafting.co.pem.key')
	context.use_certificate_file('security/soulcrafting.co.crt')
	application.run(debug = True, ssl_context=context)


@manager.command
def test():
	"""Run unit tests"""
	if (ENV_CONFIG != 'testing'): raise Exception('\nFailure: Running with incorrect CONFIG(' + str(ENV_CONFIG) + ') rerun as:\nINSPRITE_CONFIG=testing python ./application.py test')
	import unittest
	all_tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(all_tests)



if __name__ == "__main__":
	exec_app = manager.run

	# AWS-EB starts the server w/ no parameters.
	if (len(sys.argv) < 2): exec_app = runserver
	exec_app()
