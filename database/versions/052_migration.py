from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alembic_version = Table('alembic_version', pre_meta,
    Column('version_num', VARCHAR(length=32), nullable=False),
)

account = Table('account', pre_meta,
    Column('userid', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('email', VARCHAR(length=128), nullable=False),
    Column('name', VARCHAR(length=128), nullable=False),
    Column('pwhash', VARCHAR(length=128), nullable=False),
    Column('status', INTEGER, nullable=False),
    Column('source', INTEGER, nullable=False),
    Column('phone', VARCHAR(length=20)),
    Column('created', TIMESTAMP),
    Column('updated', TIMESTAMP),
    Column('sec_question', VARCHAR(length=128)),
    Column('sec_answer', VARCHAR(length=128)),
    Column('stripe_cust', VARCHAR(length=64)),
    Column('role', INTEGER),
    Column('email_policy', INTEGER),
    Column('referred_by', VARCHAR(length=40)),
    Column('dob', TIMESTAMP),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alembic_version'].drop()
    pre_meta.tables['account'].columns['dob'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alembic_version'].create()
    pre_meta.tables['account'].columns['dob'].create()
