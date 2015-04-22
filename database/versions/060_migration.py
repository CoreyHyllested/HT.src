from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
businessreference = Table('businessreference', post_meta,
    Column('br_uuid', String(length=40), primary_key=True, nullable=False),
    Column('br_bus_acct', String(length=40), nullable=False),
    Column('br_bus_prof', String(length=40), nullable=False),
    Column('br_req_mail', String(length=64), nullable=False),
    Column('br_req_prof', String(length=40)),
    Column('br_flags', Integer),
    Column('created', DateTime),
    Column('updated', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['businessreference'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['businessreference'].drop()
