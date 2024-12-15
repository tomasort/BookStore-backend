"""empty message

Revision ID: 5ff28fff0880
Revises: 
Create Date: 2024-12-15 11:03:07.484275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ff28fff0880'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('birth_date_str', sa.String(), nullable=True),
    sa.Column('death_date', sa.Date(), nullable=True),
    sa.Column('death_date_str', sa.String(), nullable=True),
    sa.Column('biography', sa.Text(), nullable=True),
    sa.Column('other_names', sa.JSON(), nullable=True),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('open_library_id', sa.String(), nullable=True),
    sa.Column('casa_del_libro_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('isbn_10', sa.String(), nullable=True),
    sa.Column('isbn_13', sa.String(), nullable=True),
    sa.Column('publish_date', sa.Date(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('cover_url', sa.String(), nullable=True),
    sa.Column('current_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('previous_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('price_alejandria', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('iva', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('cost_supplier', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('average_cost_alejandria', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('last_cost_alejandria', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('stock', sa.Integer(), nullable=True),
    sa.Column('stock_alejandria', sa.Integer(), nullable=True),
    sa.Column('stock_consig', sa.Integer(), nullable=True),
    sa.Column('stock_consig_alejandria', sa.Integer(), nullable=True),
    sa.Column('physical_format', sa.String(), nullable=True),
    sa.Column('number_of_pages', sa.Integer(), nullable=True),
    sa.Column('bar_code_alejandria', sa.String(), nullable=True),
    sa.Column('isbn_alejandria', sa.String(), nullable=True),
    sa.Column('code_alejandria', sa.String(), nullable=True),
    sa.Column('physical_dimensions', sa.String(), nullable=True),
    sa.Column('weight', sa.String(), nullable=True),
    sa.Column('publish_places', sa.JSON(), nullable=True),
    sa.Column('edition_name', sa.String(), nullable=True),
    sa.Column('subtitle', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_book_bar_code_alejandria'), ['bar_code_alejandria'], unique=False)
        batch_op.create_index(batch_op.f('ix_book_code_alejandria'), ['code_alejandria'], unique=False)
        batch_op.create_index(batch_op.f('ix_book_isbn_10'), ['isbn_10'], unique=True)
        batch_op.create_index(batch_op.f('ix_book_isbn_13'), ['isbn_13'], unique=True)
        batch_op.create_index(batch_op.f('ix_book_isbn_alejandria'), ['isbn_alejandria'], unique=False)

    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('language',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alejandria_code', sa.Integer(), nullable=True),
    sa.Column('cedula', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('contact_name', sa.String(), nullable=True),
    sa.Column('nombre_banco', sa.String(), nullable=True),
    sa.Column('titular_banco', sa.String(), nullable=True),
    sa.Column('rif_banco', sa.String(), nullable=True),
    sa.Column('cod_cuenta', sa.String(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('series',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book_authors',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'author_id')
    )
    op.create_table('book_genres',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )
    op.create_table('book_languages',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'language_id')
    )
    op.create_table('book_providers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'provider_id')
    )
    op.create_table('book_publishers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('publisher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'publisher_id')
    )
    op.create_table('book_series',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('series_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'series_id')
    )
    op.create_table('order_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_item')
    op.drop_table('book_series')
    op.drop_table('book_publishers')
    op.drop_table('book_providers')
    op.drop_table('book_languages')
    op.drop_table('book_genres')
    op.drop_table('book_authors')
    op.drop_table('series')
    op.drop_table('publisher')
    op.drop_table('provider')
    op.drop_table('order')
    op.drop_table('language')
    op.drop_table('genre')
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_book_isbn_alejandria'))
        batch_op.drop_index(batch_op.f('ix_book_isbn_13'))
        batch_op.drop_index(batch_op.f('ix_book_isbn_10'))
        batch_op.drop_index(batch_op.f('ix_book_code_alejandria'))
        batch_op.drop_index(batch_op.f('ix_book_bar_code_alejandria'))

    op.drop_table('book')
    op.drop_table('author')
    # ### end Alembic commands ###
