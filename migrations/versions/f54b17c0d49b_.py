"""empty message

Revision ID: f54b17c0d49b
Revises: 
Create Date: 2025-04-04 23:56:58.648450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f54b17c0d49b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('birth_date_str', sa.String(), nullable=True),
    sa.Column('death_date', sa.Date(), nullable=True),
    sa.Column('death_date_str', sa.String(), nullable=True),
    sa.Column('biography', sa.Text(), nullable=True),
    sa.Column('other_names', sa.JSON(), nullable=True),
    sa.Column('open_library_id', sa.String(), nullable=True),
    sa.Column('casa_del_libro_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('subtitle', sa.String(), nullable=True),
    sa.Column('isbn_10', sa.String(), nullable=True),
    sa.Column('isbn_13', sa.String(), nullable=True),
    sa.Column('other_isbns', sa.JSON(), nullable=True),
    sa.Column('publish_date', sa.Date(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
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
    sa.Column('rating', sa.Numeric(precision=4, scale=2), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_book_isbn_10'), ['isbn_10'], unique=True)
        batch_op.create_index(batch_op.f('ix_book_isbn_13'), ['isbn_13'], unique=True)

    op.create_table('exchange_rate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rate', sa.Float(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('genre',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('language',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('promotions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('conditions', sa.JSON(), nullable=True),
    sa.Column('discount_value', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('discount_type', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
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
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('series',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('session_token', sa.String(length=256), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('date_of_birth', sa.DateTime(), nullable=True),
    sa.Column('id_number', sa.String(length=20), nullable=True),
    sa.Column('id_type', sa.String(length=20), nullable=True),
    sa.Column('shipping_address', sa.String(length=200), nullable=True),
    sa.Column('shipping_city', sa.String(length=100), nullable=True),
    sa.Column('shipping_state', sa.String(length=100), nullable=True),
    sa.Column('shipping_country', sa.String(length=100), nullable=True),
    sa.Column('shipping_postal_code', sa.String(length=20), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('preferred_language', sa.String(length=10), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.Column('role', sa.Enum('USER', 'ADMIN', 'STAFF', name='role'), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'BANNED', name='accountstatus'), nullable=False),
    sa.Column('newsletter_subscription', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('author_photo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('size', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book_authors',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'author_id')
    )
    op.create_table('book_genres',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )
    op.create_table('book_languages',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'language_id')
    )
    op.create_table('book_providers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'provider_id')
    )
    op.create_table('book_publishers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('publisher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'publisher_id')
    )
    op.create_table('book_series',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('series_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('book_id', 'series_id')
    )
    op.create_table('cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('cover',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
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
    op.create_table('discount',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=True),
    sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('fixed_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('favorite_books',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'book_id')
    )
    op.create_table('featured_book',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('expiry_date', sa.Date(), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('featured_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('tracking_number', sa.String(length=50), nullable=True),
    sa.Column('shipping_address', sa.String(length=200), nullable=True),
    sa.Column('shipping_city', sa.String(length=100), nullable=True),
    sa.Column('shipping_state', sa.String(length=100), nullable=True),
    sa.Column('shipping_country', sa.String(length=100), nullable=True),
    sa.Column('shipping_postal_code', sa.String(length=20), nullable=True),
    sa.Column('billing_address', sa.String(length=200), nullable=True),
    sa.Column('billing_city', sa.String(length=100), nullable=True),
    sa.Column('billing_state', sa.String(length=100), nullable=True),
    sa.Column('billing_country', sa.String(length=100), nullable=True),
    sa.Column('billing_postal_code', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tax', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'PAID', 'CONFIRMED', 'SHIPPED', 'CANCELED', name='orderstatus'), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_promotions',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('promotion_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'promotion_id')
    )
    op.create_table('wishlist_books',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'book_id')
    )
    op.create_table('cart_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('in_stock', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], ),
    sa.PrimaryKeyConstraint('id')
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
    op.drop_table('cart_item')
    op.drop_table('wishlist_books')
    op.drop_table('user_promotions')
    op.drop_table('review')
    op.drop_table('order')
    op.drop_table('featured_book')
    op.drop_table('favorite_books')
    op.drop_table('discount')
    op.drop_table('cover')
    op.drop_table('cart')
    op.drop_table('book_series')
    op.drop_table('book_publishers')
    op.drop_table('book_providers')
    op.drop_table('book_languages')
    op.drop_table('book_genres')
    op.drop_table('book_authors')
    op.drop_table('author_photo')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('series')
    op.drop_table('publisher')
    op.drop_table('provider')
    op.drop_table('promotions')
    op.drop_table('language')
    op.drop_table('genre')
    op.drop_table('exchange_rate')
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_book_isbn_13'))
        batch_op.drop_index(batch_op.f('ix_book_isbn_10'))

    op.drop_table('book')
    op.drop_table('author')
    # ### end Alembic commands ###
