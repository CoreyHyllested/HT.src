import os
import imp
from migrate.versioning import api
from migrate.exceptions import *
from server.infrastructure.srvc_database import DATABASE_URI
from server.infrastructure.srvc_database import MIGRATE_REPO
from server.infrastructure.srvc_database import Base

if not os.path.exists(MIGRATE_REPO):
	raise Exception('You must first create', MIGRATE_REPO)


print 'saving the current DB model ...'
tmp_module = imp.new_module('old_model')
old_model = api.create_model(DATABASE_URI, MIGRATE_REPO)

migration = MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(DATABASE_URI, MIGRATE_REPO) + 1)
print 'next database version would be', migration

exec old_model in tmp_module.__dict__
script = api.make_update_script_for_model(DATABASE_URI, MIGRATE_REPO, tmp_module.meta, Base.metadata)
open(migration, "wt").write(script)

api.upgrade(DATABASE_URI, MIGRATE_REPO)
print 'New migration saved as ' + migration
print 'Current database version: ' + str(api.db_version(DATABASE_URI, MIGRATE_REPO))
