#!/usr/bin/env python
import os
from server import  initialize_server
from flask.ext.script import Manager, Shell
from OpenSSL import SSL

application = initialize_server(os.getenv('INSPRITE_CONFIG') or 'default')
manager = Manager(application)

def mk_insprite_shell_ctx():
	return dict(app=application)

manager.add_command("shell", Shell(make_context=mk_insprite_shell_ctx))

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('security/herotime-pk.pem')
context.use_certificate_file('security/herotime.crt')


def main():
	application.run(debug = True, ssl_context=context)


if __name__ == "__main__":
	manager.run()
