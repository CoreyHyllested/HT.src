#!/opt/HeroTime/dev/bin/python

from migrate.versioning import api
from server.infrastructure.srvc_database import SQLALCHEMY_DATABASE_URI
from server.infrastructure.srvc_database import SQLALCHEMY_MIGRATE_REPO
from server.infrastructure.srvc_database import init_db
import os.path

init_db()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
