from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
lesson = Table('lesson', pre_meta,
    Column('lesson_id', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('lesson_profile', VARCHAR(length=40), nullable=False),
    Column('lesson_created', TIMESTAMP, nullable=False),
    Column('lesson_flags', INTEGER),
    Column('lesson_address_1', VARCHAR(length=64)),
    Column('lesson_address_2', VARCHAR(length=64)),
    Column('lesson_address_details', VARCHAR(length=256)),
    Column('lesson_avail', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['lesson'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['lesson'].create()
