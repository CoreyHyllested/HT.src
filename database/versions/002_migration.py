from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
oauth = Table('oauth', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ht_account', String(length=40), nullable=False),
    Column('oa_account', String(length=64), nullable=False),
    Column('oa_service', Integer, nullable=False),
    Column('oa_flags', Integer, nullable=False),
    Column('oa_email', String(length=128)),
    Column('oa_token', String(length=64)),
    Column('oa_secret', String(length=64)),
    Column('oa_optdata1', String(length=256)),
    Column('oa_optdata2', String(length=256)),
    Column('oa_optdata3', String(length=256)),
    Column('oa_created', DateTime),
    Column('oa_ts_login', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['oauth'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['oauth'].drop()
