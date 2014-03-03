from __future__ import absolute_import
from server.infrastructure.srvc_events   import mngr
from server.infrastructure.srvc_database import init_db

if __name__ == "__main__":
#	print 'start db'
#	init_db()
#	mngr.init_db()
	print 'start manager'
	mngr.start()
