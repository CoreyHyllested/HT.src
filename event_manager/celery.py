from __future__ import absolute_import
from server.infrastructure.srvc_events   import mngr
from server.infrastructure.srvc_database import *

if __name__ == "__main__":
#	mngr.init_db()
	print 'start manager'
	mngr.start()
