from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
image_lesson_map = Table('image_lesson_map', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('map_image', VARCHAR(length=64), nullable=False),
    Column('map_lesson', VARCHAR(length=40), nullable=False),
    Column('map_prof', VARCHAR(length=40)),
    Column('map_comm', VARCHAR(length=256)),
    Column('map_order', INTEGER, nullable=False),
)

meeting = Table('meeting', pre_meta,
    Column('meet_id', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('meet_sellr', VARCHAR(length=40), nullable=False),
    Column('meet_buyer', VARCHAR(length=40), nullable=False),
    Column('meet_owner', VARCHAR(length=40), nullable=False),
    Column('meet_state', INTEGER, nullable=False),
    Column('meet_flags', INTEGER, nullable=False),
    Column('meet_count', INTEGER, nullable=False),
    Column('meet_cost', INTEGER, nullable=False),
    Column('meet_ts', TIMESTAMP(timezone=True), nullable=False),
    Column('meet_tf', TIMESTAMP(timezone=True), nullable=False),
    Column('meet_tz', VARCHAR(length=32), nullable=False),
    Column('meet_details', VARCHAR(length=2048), nullable=False),
    Column('meet_location', VARCHAR(length=1024), nullable=False),
    Column('meet_created', TIMESTAMP, nullable=False),
    Column('meet_updated', TIMESTAMP, nullable=False),
    Column('meet_secured', TIMESTAMP),
    Column('meet_charged', TIMESTAMP),
    Column('charge_customer_id', VARCHAR(length=40)),
    Column('charge_credit_card', VARCHAR(length=40)),
    Column('charge_transaction', VARCHAR(length=40)),
    Column('charge_user_token', VARCHAR(length=40)),
    Column('hero_deposit_acct', VARCHAR(length=40)),
    Column('review_buyer', VARCHAR(length=40)),
    Column('review_sellr', VARCHAR(length=40)),
    Column('meet_lesson', VARCHAR(length=40)),
    Column('meet_groupsize', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['image_lesson_map'].drop()
    pre_meta.tables['meeting'].columns['meet_lesson'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['image_lesson_map'].create()
    pre_meta.tables['meeting'].columns['meet_lesson'].create()
