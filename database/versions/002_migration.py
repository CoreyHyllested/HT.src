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
)

appointment = Table('appointment', post_meta,
    Column('apptid', String(length=40), primary_key=True, nullable=False),
    Column('buyer_prof', String(length=40), nullable=False),
    Column('sellr_prof', String(length=40), nullable=False),
    Column('status', Integer, default=ColumnDefault(0)),
    Column('location', String(length=1000), nullable=False),
    Column('ts_begin', DateTime, nullable=False),
    Column('ts_finish', DateTime, nullable=False),
    Column('cost', Integer, nullable=False),
    Column('paid', Boolean, default=ColumnDefault(False)),
    Column('cust', String(length=20), nullable=False),
    Column('description', String(length=3000)),
    Column('transaction', String(length=40)),
    Column('created', DateTime, nullable=False),
    Column('updated', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 13, 6, 3, 213472))),
    Column('agreement', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 13, 6, 3, 213523))),
    Column('reviewOfBuyer', String(length=40)),
    Column('reviewOfSellr', String(length=40)),
)

image = Table('image', post_meta,
    Column('img_id', String(length=64), primary_key=True, nullable=False),
    Column('img_profile', String(length=40), nullable=False),
    Column('img_comment', String(length=256)),
    Column('img_created', DateTime),
    Column('img_flags', Integer, default=ColumnDefault(0)),
    Column('img_order', Integer, nullable=False, default=ColumnDefault(0)),
)

industry = Table('industry', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=80), nullable=False),
)

oauth = Table('oauth', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ht_account', String(length=40), nullable=False),
    Column('oa_account', String(length=64), nullable=False),
    Column('oa_service', Integer, nullable=False),
    Column('oa_flags', Integer, nullable=False),
    Column('oa_email', String(length=128)),
    Column('oa_token', String(length=256)),
    Column('oa_secret', String(length=64)),
    Column('oa_optdata1', String(length=256)),
    Column('oa_optdata2', String(length=256)),
    Column('oa_optdata3', String(length=256)),
    Column('oa_created', DateTime),
    Column('oa_ts_login', DateTime),
)

profile = Table('profile', post_meta,
    Column('prof_id', String(length=40), primary_key=True, nullable=False),
    Column('account', String(length=40), nullable=False),
    Column('prof_name', String(length=128), nullable=False),
    Column('prof_vanity', String(length=128)),
    Column('rating', Float, nullable=False, default=ColumnDefault(-1)),
    Column('reviews', Integer, nullable=False, default=ColumnDefault(0)),
    Column('prof_img', String(length=128), nullable=False, default=ColumnDefault('no_pic_big.svg')),
    Column('prof_url', String(length=128), default=ColumnDefault('http://herotime.co')),
    Column('prof_bio', String(length=5000), default=ColumnDefault('About me')),
    Column('prof_tz', String(length=20)),
    Column('prof_rate', Integer, nullable=False, default=ColumnDefault(40)),
    Column('industry', String(length=64)),
    Column('headline', String(length=128)),
    Column('location', String(length=64), nullable=False, default=ColumnDefault('Berkeley, CA')),
    Column('updated', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 19, 6, 3, 204705))),
    Column('created', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 19, 6, 3, 204743))),
)

proposal = Table('proposal', post_meta,
    Column('prop_uuid', String(length=40), primary_key=True, nullable=False),
    Column('prop_hero', String(length=40), nullable=False),
    Column('prop_user', String(length=40), nullable=False),
    Column('prop_state', Integer, nullable=False, default=ColumnDefault(1)),
    Column('prop_flags', Integer, nullable=False, default=ColumnDefault(0)),
    Column('prop_count', Integer, nullable=False, default=ColumnDefault(0)),
    Column('prop_cost', Integer, nullable=False, default=ColumnDefault(0)),
    Column('prop_from', String(length=40), nullable=False),
    Column('prop_ts', DateTime(timezone=True), nullable=False),
    Column('prop_tf', DateTime(timezone=True), nullable=False),
    Column('prop_tz', String(length=20)),
    Column('prop_desc', String(length=3000)),
    Column('prop_place', String(length=1000), nullable=False),
    Column('prop_created', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 19, 6, 3, 208081))),
    Column('prop_updated', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 19, 6, 3, 208120))),
    Column('appt_secured', DateTime),
    Column('appt_charged', DateTime),
    Column('challengeID', String(length=40), nullable=False),
    Column('charge_customer_id', String(length=40)),
    Column('charge_credit_card', String(length=40)),
    Column('charge_transaction', String(length=40)),
    Column('charge_user_token', String(length=40)),
    Column('hero_deposit_acct', String(length=40)),
    Column('review_hero', String(length=40)),
    Column('review_user', String(length=40)),
)

review = Table('review', post_meta,
    Column('review_id', String(length=40), primary_key=True, nullable=False),
    Column('prof_reviewed', String(length=40), nullable=False),
    Column('prof_authored', String(length=40), nullable=False),
    Column('rev_status', Integer, default=ColumnDefault(1)),
    Column('rev_appt', String(length=40), nullable=False),
    Column('rev_twin', String(length=40)),
    Column('appt_score', Integer, nullable=False, default=ColumnDefault(-1)),
    Column('appt_value', Integer, nullable=False, default=ColumnDefault(-1)),
    Column('score_attr_time', Integer),
    Column('score_attr_comm', Integer),
    Column('generalcomments', String(length=5000)),
    Column('rev_updated', DateTime, nullable=False, default=ColumnDefault(datetime.datetime(2014, 6, 12, 19, 6, 3, 223437))),
    Column('rev_flags', Integer, default=ColumnDefault(0)),
)

skills = Table('skills', post_meta,
    Column('skill_id', Integer, primary_key=True, nullable=False),
    Column('skill_name', String(length=80), nullable=False),
    Column('skill_prof', String(length=40), nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['account'].create()
    post_meta.tables['appointment'].create()
    post_meta.tables['image'].create()
    post_meta.tables['industry'].create()
    post_meta.tables['oauth'].create()
    post_meta.tables['profile'].create()
    post_meta.tables['proposal'].create()
    post_meta.tables['review'].create()
    post_meta.tables['skills'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['account'].drop()
    post_meta.tables['appointment'].drop()
    post_meta.tables['image'].drop()
    post_meta.tables['industry'].drop()
    post_meta.tables['oauth'].drop()
    post_meta.tables['profile'].drop()
    post_meta.tables['proposal'].drop()
    post_meta.tables['review'].drop()
    post_meta.tables['skills'].drop()
