from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
availability = Table('availability', post_meta,
    Column('avail_id', Integer, primary_key=True, nullable=False),
    Column('avail_profile', String(length=40), nullable=False),
    Column('avail_created', DateTime, nullable=False),
    Column('avail_updated', DateTime, nullable=False),
    Column('avail_weekday', Integer),
    Column('avail_repeats', Integer),
    Column('avail_timeout', DateTime),
    Column('avail_start', Time),
    Column('avail_finish', Time),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['availability'].columns['avail_finish'].create()
    post_meta.tables['availability'].columns['avail_start'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['availability'].columns['avail_finish'].drop()
    post_meta.tables['availability'].columns['avail_start'].drop()
