from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
availability = Table('availability', pre_meta,
    Column('avail_id', INTEGER, primary_key=True, nullable=False),
    Column('avail_profile', VARCHAR(length=40), nullable=False),
    Column('avail_created', TIMESTAMP, nullable=False),
    Column('avail_updated', TIMESTAMP, nullable=False),
    Column('avail_weekday', INTEGER),
    Column('avail_start', TIMESTAMP),
    Column('avail_finish', TIMESTAMP),
    Column('avail_repeats', INTEGER),
    Column('avail_timeout', TIMESTAMP),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['availability'].columns['avail_finish'].drop()
    pre_meta.tables['availability'].columns['avail_start'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['availability'].columns['avail_finish'].create()
    pre_meta.tables['availability'].columns['avail_start'].create()
