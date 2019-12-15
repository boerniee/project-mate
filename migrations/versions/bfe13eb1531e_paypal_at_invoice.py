"""paypal at invoice

Revision ID: bfe13eb1531e
Revises: 0ab518b280e7
Create Date: 2019-12-14 14:50:21.289242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfe13eb1531e'
down_revision = '0ab518b280e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoice', sa.Column('paypalme', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invoice', 'paypalme')
    # ### end Alembic commands ###
