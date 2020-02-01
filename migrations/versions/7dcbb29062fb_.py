""" Rename Drink to product

Revision ID: 7dcbb29062fb
Revises: 48546fdb930b
Create Date: 2020-01-26 10:42:00.044207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7dcbb29062fb'
down_revision = '48546fdb930b'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('drink', 'product')
    op.alter_column('consumption', 'drink_id', new_column_name='product_id')

def downgrade():
    op.rename_table('product', 'drink')
    op.alter_column('consumption', 'product_id', new_column_name='drink_id')
