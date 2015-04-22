from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
industry = Table('industry', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=80), nullable=False),
)

registrant = Table('registrant', pre_meta,
    Column('reg_userid', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('reg_email', VARCHAR(length=128)),
    Column('reg_location', VARCHAR(length=128)),
    Column('reg_ip', VARCHAR(length=20)),
    Column('reg_name', VARCHAR(length=128)),
    Column('reg_org', VARCHAR(length=128)),
    Column('reg_referrer', VARCHAR(length=128)),
    Column('reg_flags', INTEGER),
    Column('reg_created', TIMESTAMP),
    Column('reg_updated', TIMESTAMP),
    Column('reg_comment', VARCHAR(length=1024)),
    Column('reg_referral_code', VARCHAR(length=128)),
)

skills = Table('skills', pre_meta,
    Column('skill_id', INTEGER, primary_key=True, nullable=False),
    Column('skill_name', VARCHAR(length=80), nullable=False),
    Column('skill_prof', VARCHAR(length=40), nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['industry'].drop()
    pre_meta.tables['registrant'].drop()
    pre_meta.tables['skills'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['industry'].create()
    pre_meta.tables['registrant'].create()
    pre_meta.tables['skills'].create()
