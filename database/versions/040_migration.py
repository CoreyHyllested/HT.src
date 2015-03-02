from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
project = Table('project', post_meta,
    Column('proj_id', String(length=40), primary_key=True, nullable=False),
    Column('account', String(length=40), nullable=False),
    Column('proj_name', String(length=128), nullable=False),
    Column('proj_addr', String(length=256)),
    Column('proj_desc', String(length=5000)),
    Column('timeline', String(length=256)),
    Column('proj_min', Integer),
    Column('proj_max', Integer),
    Column('proj_review', Integer, default=ColumnDefault(-1)),
    Column('contact', String(length=20)),
    Column('updated', DateTime, nullable=False, default=ColumnDefault('')),
    Column('created', DateTime, nullable=False, default=ColumnDefault('')),
    Column('availability', Integer, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].drop()
