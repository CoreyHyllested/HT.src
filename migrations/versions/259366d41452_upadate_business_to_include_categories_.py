"""upadate Business to include categories for breadcrumbs

Revision ID: 259366d41452
Revises: 4fddf47bf550
Create Date: 2015-09-04 12:00:33.330687

"""

# revision identifiers, used by Alembic.
revision = '259366d41452'
down_revision = '4fddf47bf550'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('bus_category', sa.String(length=140), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('business', 'bus_category')
    ### end Alembic commands ###