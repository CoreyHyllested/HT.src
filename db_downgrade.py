#!/opt/HeroTime/dev/bin/python

from migrate.versioning import api
from server.infrastructure.srvc_database import SQLALCHEMY_DATABASE_URI
from server.infrastructure.srvc_database import SQLALCHEMY_MIGRATE_REPO
from server.infrastructure.srvc_database import Base, init_db

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))
