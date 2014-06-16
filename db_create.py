#!/opt/HeroTime/dev/bin/python

import os
import imp
from migrate.versioning import api
from migrate.exceptions import *
from server.infrastructure.srvc_database import DATABASE_URI
from server.infrastructure.srvc_database import MIGRATE_REPO
from server.infrastructure.srvc_database import Base

print 'Checking if', MIGRATE_REPO, 'exists'

empty_module = imp.new_module('empty_model')
old_model = api.create_model(DATABASE_URI, MIGRATE_REPO)

Base.metadata.create_all()

if not os.path.exists(MIGRATE_REPO):
	api.create(MIGRATE_REPO, 'database repository')
	api.version_control(DATABASE_URI, MIGRATE_REPO)

	migration_script = MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(DATABASE_URI, MIGRATE_REPO))
	exec old_model in empty_module.__dict__
	script = api.make_update_script_for_model(DATABASE_URI, MIGRATE_REPO, empty_module.meta, Base.metadata)
	open(migration_script, "wt").write(script)
else:
	try:
		api.version_control(DATABASE_URI, MIGRATE_REPO, api.version(MIGRATE_REPO))
		migration_script = MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(DATABASE_URI, MIGRATE_REPO))

		exec old_model in empty_module.__dict__
		script = api.make_update_script_for_model(DATABASE_URI, MIGRATE_REPO, empty_module.meta, Base.metadata)
		open(migration_script, "wt").write(script)
	except DatabaseAlreadyControlledError as e:
		print 'expected.. db already versioned'
	except Exception as e:
		print 'hmmm.'
		print e
