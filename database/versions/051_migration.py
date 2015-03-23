from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
giftcertificate = Table('giftcertificate', post_meta,
    Column('gift_id', String(length=40), primary_key=True, nullable=False),
    Column('gift_state', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_value', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_flags', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_recipient_name', String(length=64)),
    Column('gift_recipient_mail', String(length=64), nullable=False),
    Column('gift_recipient_cell', String(length=16)),
    Column('gift_recipient_addr', String(length=128)),
    Column('gift_recipient_note', String(length=256)),
    Column('gift_recipient_proj', String(length=40)),
    Column('gift_recipient_prof', String(length=40)),
    Column('gift_purchaser_name', String(length=64), nullable=False),
    Column('gift_purchaser_mail', String(length=64), nullable=False),
    Column('gift_purchaser_cost', Integer, nullable=False, default=ColumnDefault(0)),
    Column('gift_purchaser_prof', String(length=40)),
    Column('gift_stripe_transaction', String(length=40)),
    Column('gift_stripe_chargetoken', String(length=40)),
    Column('gift_stripe_creditcard', String(length=40)),
    Column('gift_stripe_customerid', String(length=40)),
    Column('gift_dt_created', DateTime, nullable=False),
    Column('gift_dt_updated', DateTime, nullable=False),
    Column('gift_dt_charged', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['giftcertificate'].columns['gift_dt_created'].create()
    post_meta.tables['giftcertificate'].columns['gift_dt_updated'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['giftcertificate'].columns['gift_dt_created'].drop()
    post_meta.tables['giftcertificate'].columns['gift_dt_updated'].drop()
