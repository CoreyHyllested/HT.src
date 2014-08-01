from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
account = Table('account', post_meta,
    Column('userid', String(length=40), primary_key=True, nullable=False),
    Column('email', String(length=128), nullable=False),
    Column('name', String(length=128), nullable=False),
    Column('pwhash', String(length=128), nullable=False),
    Column('status', Integer, nullable=False, default=ColumnDefault(0)),
    Column('source', Integer, nullable=False, default=ColumnDefault(0)),
    Column('phone', String(length=20)),
    Column('dob', DateTime),
    Column('created', DateTime),
    Column('updated', DateTime),
    Column('sec_question', String(length=128)),
    Column('sec_answer', String(length=128)),
    Column('stripe_cust', String(length=64)),
    Column('role', Integer, default=ColumnDefault(0)),
    Column('email_policy', Integer, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['account'].columns['email_policy'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['account'].columns['email_policy'].drop()
