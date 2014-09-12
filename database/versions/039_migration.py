from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
meeting = Table('meeting', post_meta,
    Column('meet_id', String(length=40), primary_key=True, nullable=False),
    Column('meet_sellr', String(length=40), nullable=False),
    Column('meet_buyer', String(length=40), nullable=False),
    Column('meet_owner', String(length=40), nullable=False),
    Column('meet_state', Integer, nullable=False, default=ColumnDefault(0)),
    Column('meet_flags', Integer, nullable=False, default=ColumnDefault(0)),
    Column('meet_count', Integer, nullable=False, default=ColumnDefault(0)),
    Column('meet_cost', Integer, nullable=False, default=ColumnDefault(0)),
    Column('meet_ts', DateTime(timezone=True), nullable=False),
    Column('meet_tf', DateTime(timezone=True), nullable=False),
    Column('meet_tz', String(length=32), nullable=False),
    Column('meet_details', String(length=2048), nullable=False),
    Column('meet_location', String(length=1024), nullable=False),
    Column('meet_created', DateTime, nullable=False),
    Column('meet_updated', DateTime, nullable=False),
    Column('meet_secured', DateTime),
    Column('meet_charged', DateTime),
    Column('charge_customer_id', String(length=40)),
    Column('charge_credit_card', String(length=40)),
    Column('charge_transaction', String(length=40)),
    Column('charge_user_token', String(length=40)),
    Column('hero_deposit_acct', String(length=40)),
    Column('review_buyer', String(length=40)),
    Column('review_sellr', String(length=40)),
    Column('meet_lesson', String(length=40)),
    Column('meet_groupsize', Integer, default=ColumnDefault(1)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['meeting'].columns['meet_lesson'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['meeting'].columns['meet_lesson'].drop()
