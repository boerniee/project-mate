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

def consumption2():
    meta = sa.MetaData()
    return sa.Table(
        'consumption',meta,
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('drink_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('time', sa.DateTime(), nullable=True),
        sa.Column('billed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['drink_id'], ['drink.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def consumption():
    meta = sa.MetaData()
    return sa.Table(
        'consumption',meta,
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('time', sa.DateTime(), nullable=True),
        sa.Column('billed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def upgrade():
    op.rename_table('drink', 'product')

    bind = op.get_bind()
    if bind.engine.name == 'mysql':
        op.alter_column('consumption', 'drink_id', new_column_name='product_id', type_=sa.Integer())
        op.drop_constraint(u'consumption_ibfk_1', 'consumption', type_='foreignkey')
        op.create_foreign_key(u'consumption_ibfk_1', 'consumption', 'product', ['product_id'], ['id'])
    else:
        with op.batch_alter_table('consumption', copy_from=consumption2()) as bop:
            bop.alter_column('drink_id', new_column_name='product_id')


def downgrade():
    op.rename_table('product', 'drink')
    bind = op.get_bind()
    if bind.engine.name == 'mysql':
        op.alter_column('consumption', 'product_id', new_column_name='drink_id', type_=sa.Integer())
        op.drop_constraint(u'consumption_ibfk_1', 'consumption', type_='foreignkey')
        op.create_foreign_key(u'consumption_ibfk_1', 'consumption', 'drink', ['drink_id'], ['id'])
    else:
        with op.batch_alter_table('consumption', copy_from=consumption()) as bop:
            bop.alter_column('product_id', new_column_name='drink_id')
