from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
lesson = Table('lesson', post_meta,
    Column('lesson_id', String(length=40), primary_key=True, nullable=False),
    Column('lesson_profile', String(length=40), nullable=False),
    Column('lesson_title', String(length=128), nullable=False),
    Column('lesson_description', String(length=5000)),
    Column('lesson_industry', String(length=64), nullable=False),
    Column('lesson_hourly_rate', Integer),
    Column('lesson_lesson_rate', Integer),
    Column('lesson_avail', Integer, nullable=False, default=ColumnDefault(0)),
    Column('lesson_duration', Integer),
    Column('lesson_loc_option', Integer, nullable=False, default=ColumnDefault(0)),
    Column('lesson_address_1', String(length=64)),
    Column('lesson_address_2', String(length=64)),
    Column('lesson_city', String(length=64)),
    Column('lesson_state', String(length=10)),
    Column('lesson_zip', String(length=10)),
    Column('lesson_country', String(length=64)),
    Column('lesson_address_details', String(length=256)),
    Column('lesson_updated', DateTime, nullable=False),
    Column('lesson_created', DateTime, nullable=False),
    Column('lesson_flags', Integer, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['lesson'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['lesson'].drop()
