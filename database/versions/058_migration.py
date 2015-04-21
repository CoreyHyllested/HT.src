from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
profile = Table('profile', post_meta,
    Column('prof_id', String(length=40), primary_key=True, nullable=False),
    Column('account', String(length=40), nullable=False),
    Column('prof_name', String(length=128), nullable=False),
    Column('prof_img', String(length=128), nullable=False, default=ColumnDefault('no_pic_big.svg')),
    Column('prof_url', String(length=128), default=ColumnDefault('https://soulcrafting.co')),
    Column('prof_bio', String(length=5000), default=ColumnDefault('About me')),
    Column('prof_tz', String(length=20)),
    Column('prof_phone', String(length=20)),
    Column('prof_email', String(length=64)),
    Column('industry', String(length=64)),
    Column('headline', String(length=128)),
    Column('location', String(length=64), nullable=False, default=ColumnDefault('Boulder, CO')),
    Column('updated', DateTime, nullable=False, default=ColumnDefault('')),
    Column('created', DateTime, nullable=False, default=ColumnDefault('')),
    Column('availability', Integer, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['profile'].columns['prof_email'].create()
    post_meta.tables['profile'].columns['prof_phone'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['profile'].columns['prof_email'].drop()
    post_meta.tables['profile'].columns['prof_phone'].drop()
