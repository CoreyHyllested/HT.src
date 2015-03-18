from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
giftcertificate = Table('giftcertificate', pre_meta,
    Column('gift_id', VARCHAR(length=40), primary_key=True, nullable=False),
    Column('gift_state', INTEGER, nullable=False),
    Column('gift_value', INTEGER, nullable=False),
    Column('gift_flags', INTEGER, nullable=False),
    Column('gift_created', TIMESTAMP, nullable=False),
    Column('gift_updated', TIMESTAMP, nullable=False),
    Column('gift_charged', TIMESTAMP),
    Column('recipient_name', VARCHAR(length=64), nullable=False),
    Column('recipient_mail', VARCHAR(length=64)),
    Column('recipient_cell', VARCHAR(length=16)),
    Column('recipient_addr', VARCHAR(length=128)),
    Column('recipient_note', VARCHAR(length=256)),
    Column('recipient_proj', VARCHAR(length=40)),
    Column('recipient_prof', VARCHAR(length=40)),
    Column('gift_purchaser_name', VARCHAR(length=64)),
    Column('gift_purchaser_mail', VARCHAR(length=64)),
    Column('gift_stripe_creditcard', VARCHAR(length=40)),
    Column('gift_stripe_customerid', VARCHAR(length=40)),
    Column('gift_stripe_amountpaid', INTEGER),
    Column('gift_stripe_transaction', VARCHAR(length=40)),
    Column('gift_stripe_chargetoken', VARCHAR(length=40)),
    Column('gift_purchaser_cost', INTEGER, nullable=False),
)

giftcertificate = Table('giftcertificate', post_meta,
    Column('gift_id', String(length=40), primary_key=True, nullable=False),
    Column('gift_state', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_value', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_flags', Integer, nullable=False, default=ColumnDefault(0)),
    Column('recipient_name', String(length=64), nullable=False),
    Column('recipient_mail', String(length=64)),
    Column('recipient_cell', String(length=16)),
    Column('recipient_addr', String(length=128)),
    Column('recipient_note', String(length=256)),
    Column('recipient_proj', String(length=40)),
    Column('recipient_prof', String(length=40)),
    Column('gift_purchaser_name', String(length=64), nullable=False),
    Column('gift_purchaser_mail', String(length=64), nullable=False),
    Column('gift_purchaser_cost', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_purchaser_prof', String(length=40)),
    Column('gift_stripe_transaction', String(length=40)),
    Column('gift_stripe_chargetoken', String(length=40)),
    Column('gift_stripe_creditcard', String(length=40)),
    Column('gift_stripe_customerid', String(length=40)),
    Column('gift_created', DateTime, nullable=False),
    Column('gift_updated', DateTime, nullable=False),
    Column('gift_charged', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['giftcertificate'].columns['gift_stripe_amountpaid'].drop()
    post_meta.tables['giftcertificate'].columns['gift_purchaser_prof'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['giftcertificate'].columns['gift_stripe_amountpaid'].create()
    post_meta.tables['giftcertificate'].columns['gift_purchaser_prof'].drop()
