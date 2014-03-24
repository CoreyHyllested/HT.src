#!/usr/bin/env python

from server import application
from OpenSSL import SSL


context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('security/herotime-pk.pem')
context.use_certificate_file('security/herotime.crt')


def main():
	from server.infrastructure.srvc_database import init_db
	init_db()
	application.run(debug = True, ssl_context=context)


if __name__ == "__main__":
	main()
