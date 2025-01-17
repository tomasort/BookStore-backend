"""empty message

Revision ID: 92921b6c8db4
Revises: b7401213e916
Create Date: 2025-01-17 04:36:04.380169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92921b6c8db4'
down_revision = 'b7401213e916'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('in_stock', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_column('in_stock')

    # ### end Alembic commands ###
