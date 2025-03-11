"""empty message

Revision ID: 3d905e3ca0dc
Revises: be28b7e06f45
Create Date: 2025-03-07 11:45:16.706852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d905e3ca0dc'
down_revision = 'be28b7e06f45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cover',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('cover_type', sa.String(), nullable=True),
    sa.Column('size', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('other_isbns', sa.JSON(), nullable=True))
        batch_op.drop_column('cover_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_url', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('other_isbns')

    op.drop_table('cover')
    # ### end Alembic commands ###
