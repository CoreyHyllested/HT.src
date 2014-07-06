from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
image = Table('image', post_meta,
    Column('img_id', String(length=64), primary_key=True, nullable=False),
    Column('img_profile', String(length=40), nullable=False),
    Column('img_comment', String(length=256)),
    Column('img_created', DateTime),
    Column('img_flags', Integer, default=ColumnDefault(0)),
    Column('img_order', Integer, nullable=False, default=ColumnDefault(0)),
    Column('img_lesson', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['image'].columns['img_lesson'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['image'].columns['img_lesson'].drop()
