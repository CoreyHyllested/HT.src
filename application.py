#!/usr/bin/env python
import os, sys
from server import  initialize_server
from flask.ext.script import Manager, Shell
from OpenSSL import SSL


application = initialize_server(os.getenv('INSPRITE_CONFIG') or 'default')



def run_manager():
	def mk_insprite_shell_ctx():
		return dict(app=application)

	manager = Manager(application)
	manager.add_command("shell", Shell(make_context=mk_insprite_shell_ctx))
	manager.run()


def main():
	print 'Run with SSH'
	context = SSL.Context(SSL.SSLv23_METHOD)
	context.use_privatekey_file('security/herotime-pk.pem')
	context.use_certificate_file('security/herotime.crt')
	application.run(debug = True, ssl_context=context)




if __name__ == "__main__":
	if (len(sys.argv) >= 2):
		run_manager()
	else:
		main()
