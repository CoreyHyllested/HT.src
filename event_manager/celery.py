from __future__ import absolute_import
from flask import Flask
from config import server_configuration
from server.infrastructure.srvc_database import initialize_database
import os


ENV_CONFIG	= os.getenv('INSPRITE_CONFIG', 'development')
if (ENV_CONFIG == 'devel_money'):
	print "\n\n\n\nI too like to live dangerously.\n Serious.\nYou're entering the DangerZone"


# Seems like we're duplicating code here, but it works.
ht_unused = Flask(__name__)
ht_unused.config.from_object(server_configuration[ENV_CONFIG])
if (ENV_CONFIG== 'production' or ENV_CONFIG== 'devel_money'):
	print 'using configuration... ', ENV_CONFIG


# must init db_session, Base prior to importing event manager
initialize_database(ht_unused.config)
from server.infrastructure.srvc_events   import mngr

if __name__ == "__main__":
	print 'start manager'
	mngr.start()


