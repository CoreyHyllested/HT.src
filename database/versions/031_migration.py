from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
email = Table('email', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ht_account', String(length=40), nullable=False),
    Column('email', String(length=128), nullable=False),
    Column('flags', Integer),
    Column('created', DateTime),
)

image_lesson_map = Table('image_lesson_map', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('map_image', String(length=64), nullable=False),
    Column('map_lesson', String(length=40), nullable=False),
    Column('map_prof', String(length=40)),
    Column('map_comm', String(length=256)),
    Column('map_order', Integer, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['email'].create()
    post_meta.tables['image_lesson_map'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['email'].drop()
    post_meta.tables['image_lesson_map'].drop()
