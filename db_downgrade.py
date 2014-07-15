#!/opt/HeroTime/dev/bin/python

from migrate.versioning import api
from migrate.exceptions import *
from server import initialize_server

ht_server = initialize_server('default')
from server.infrastructure.srvc_database import DATABASE_URI
from server.infrastructure.srvc_database import MIGRATE_REPO

v = api.db_version(DATABASE_URI, MIGRATE_REPO)
api.downgrade(DATABASE_URI, MIGRATE_REPO, v - 1)
print 'Current database version: ' + str(api.db_version(DATABASE_URI, MIGRATE_REPO))
