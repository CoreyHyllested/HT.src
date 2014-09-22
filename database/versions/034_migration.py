from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
registrant = Table('registrant', post_meta,
    Column('reg_userid', String(length=40), primary_key=True, nullable=False),
    Column('reg_email', String(length=128)),
    Column('reg_location', String(length=128)),
    Column('reg_ip', String(length=20)),
    Column('reg_name', String(length=128)),
    Column('reg_org', String(length=128)),
    Column('reg_referrer', String(length=128)),
    Column('reg_flags', Integer, default=ColumnDefault(0)),
    Column('reg_created', DateTime),
    Column('reg_updated', DateTime),
    Column('reg_comment', String(length=1024)),
    Column('reg_referral_code', String(length=128)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['registrant'].columns['reg_referral_code'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['registrant'].columns['reg_referral_code'].drop()
