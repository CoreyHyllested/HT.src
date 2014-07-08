#!/opt/HeroTime/dev/bin/python

from migrate.versioning import api
from migrate.exceptions import *
from server.infrastructure.srvc_database import DATABASE_URI
from server.infrastructure.srvc_database import MIGRATE_REPO
from server.infrastructure.srvc_database import Base

api.upgrade(DATABASE_URI, MIGRATE_REPO)
print 'Current database version: ' + str(api.db_version(DATABASE_URI, MIGRATE_REPO))
