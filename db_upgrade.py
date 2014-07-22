#!/opt/HeroTime/dev/bin/python

from migrate.versioning import api
from migrate.exceptions import *
from server import initialize_server

ht_server = initialize_server('default')
from server.infrastructure.srvc_database import DATABASE_URI
from server.infrastructure.srvc_database import MIGRATE_REPO

api.upgrade(DATABASE_URI, MIGRATE_REPO)
print 'Current database version: ' + str(api.db_version(DATABASE_URI, MIGRATE_REPO))
