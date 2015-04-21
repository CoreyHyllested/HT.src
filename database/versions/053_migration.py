from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
profile = Table('profile', pre_meta,
    Column('prof_id', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('account', VARCHAR(length=40), nullable=False),
    Column('prof_name', VARCHAR(length=128), nullable=False),
    Column('prof_vanity', VARCHAR(length=128)),
    Column('rating', Float, nullable=False, default=ColumnDefault(-1)),
    Column('reviews', INTEGER, nullable=False),
    Column('prof_img', VARCHAR(length=128), nullable=False),
    Column('prof_url', VARCHAR(length=128)),
    Column('prof_bio', VARCHAR(length=5000)),
    Column('prof_tz', VARCHAR(length=20)),
    Column('prof_rate', INTEGER, nullable=False),
    Column('industry', VARCHAR(length=64)),
    Column('headline', VARCHAR(length=128)),
    Column('location', VARCHAR(length=64), nullable=False),
    Column('updated', TIMESTAMP, nullable=False),
    Column('created', TIMESTAMP, nullable=False),
    Column('availability', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['profile'].columns['prof_rate'].drop()
    pre_meta.tables['profile'].columns['prof_vanity'].drop()
    pre_meta.tables['profile'].columns['rating'].drop()
    pre_meta.tables['profile'].columns['reviews'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['profile'].columns['prof_rate'].create()
    pre_meta.tables['profile'].columns['prof_vanity'].create()
    pre_meta.tables['profile'].columns['rating'].create()
    pre_meta.tables['profile'].columns['reviews'].create()
