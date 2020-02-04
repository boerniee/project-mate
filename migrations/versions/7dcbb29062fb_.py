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
    op.alter_column('consumption', 'drink_id', new_column_name='product_id', type_=sa.Integer())
    op.drop_constraint(u'consumption_ibfk_1', 'consumption', type_='foreignkey')
    op.create_foreign_key(u'consumption_ibfk_1', 'consumption', 'product', ['product_id'], ['id'])

def downgrade():
    op.rename_table('product', 'drink')
    op.alter_column('consumption', 'product_id', new_column_name='drink_id', type_=sa.Integer())
    op.drop_constraint(u'consumption_ibfk_1', 'consumption', type_='foreignkey')
    op.create_foreign_key(u'consumption_ibfk_1', 'consumption', 'drink', ['drink_id'], ['id'])
