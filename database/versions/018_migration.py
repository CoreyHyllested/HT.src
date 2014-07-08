from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
image = Table('image', pre_meta,
    Column('img_id', VARCHAR(length=64), primary_key=True, nullable=False),
    Column('img_profile', VARCHAR(length=40), nullable=False),
    Column('img_comment', VARCHAR(length=256)),
    Column('img_created', TIMESTAMP),
    Column('img_flags', INTEGER),
    Column('img_order', INTEGER, nullable=False),
    Column('img_lesson', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['image'].columns['img_lesson'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['image'].columns['img_lesson'].create()
