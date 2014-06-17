from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
umsg = Table('umsg', post_meta,
    Column('msg_id', String(length=40), primary_key=True, nullable=False),
    Column('msg_to', String(length=40), nullable=False),
    Column('msg_from', String(length=40), nullable=False),
    Column('msg_thread', String(length=40), nullable=False),
    Column('msg_parent', String(length=40)),
    Column('msg_content', String(length=1024), nullable=False),
    Column('msg_created', DateTime, nullable=False),
    Column('msg_noticed', DateTime),
    Column('msg_opened', DateTime),
    Column('msg_subject', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['umsg'].columns['msg_subject'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['umsg'].columns['msg_subject'].drop()
