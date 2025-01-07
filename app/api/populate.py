# Script for populating the database with the data from the csv
from datetime import datetime
from time import sleep
from dateutil.parser import parse
import re
from pprint import pprint
from sqlalchemy import select, and_, or_
from sqlalchemy.inspection import inspect
import click
import pandas as pd
from flask.cli import with_appcontext
from flask import current_app
from app import db
from app.api.models import Book, Author, Genre, Series, Publisher, Language, Provider
from app.api.schemas import BookSchema, AuthorSchema, GenreSchema, SeriesSchema, PublisherSchema, LanguageSchema, ProviderSchema
from app.api import api
from typing import List
import json


def deserialize_columns(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    result_df = df.copy()
    for column_name in column_names:
        result_df[column_name] = result_df[column_name].apply(json.loads)
    return result_df


def process_date(date_str):
    try:
        return parse(date_str, fuzzy=True, default=datetime.strptime("2024-01-01", "%Y-%m-%d")).strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error parsing date: {str(e)}")
        return None


def get_field_value(row, field_name, default=None):
    return row[field_name] if not pd.isna(row[field_name]) else default


def process_author(session, author_row):
    summary = author_row['summary_cdl'] if not pd.isna(author_row['summary_cdl']) else get_field_value(author_row, 'bio_ol')
    photo = author_row['image_url_cdl'] if not pd.isna(author_row['image_url_cdl']) else get_field_value(author_row, 'picture_ol')
    name = author_row['name_cdl'] if not pd.isna(author_row['name_cdl']) else get_field_value(author_row, 'name_ol', author_row['autor_nombre_alejandria'])

    try:
        death_date = process_date(author_row['death_date_ol']) if not pd.isna(author_row['death_date_ol']) else None
    except Exception as e:
        print(f"Error parsing death date: {str(e)}")
        death_date = None

    try:
        birth_date = process_date(author_row['birth_date_ol']) if not pd.isna(author_row['birth_date_ol']) else None
    except Exception as e:
        print(f"Error parsing birth date: {str(e)}")
        birth_date = None

    author_data = {
        'name': name if not pd.isna(name) else None,
        'birth_date': birth_date,
        'birth_date_str': get_field_value(author_row, 'birth_date_ol'),
        'death_date': death_date,
        'death_date_str': get_field_value(author_row, 'death_date_ol'),
        'biography': summary,
        'other_names': json.loads(author_row['other_names_ol']) if not pd.isna(author_row['other_names_ol']) else [],
        'photo_url': photo,
        'open_library_id': get_field_value(author_row, 'key_ol'),
        'casa_del_libro_id': get_field_value(author_row, 'id_cdl')
    }

    new_author_data = AuthorSchema().load(author_data)
    # Check if author already exists
    new_author = None
    if new_author_data['open_library_id']:
        new_author = session.execute(select(Author).where(Author.open_library_id == new_author_data['open_library_id'])).scalar()
    elif new_author_data['casa_del_libro_id']:
        new_author = session.execute(select(Author).where(Author.casa_del_libro_id == new_author_data['casa_del_libro_id'])).scalar()
    else:
        new_author = session.execute(select(Author).where(Author.name == new_author_data['name'])).scalar()
    if not new_author:
        # if author does not exist, create a new one
        new_author = Author(**new_author_data)
        session.add(new_author)
        session.flush()
    return new_author


def find_authors_by_id(authors_df, ids, column_name):
    """Helper function to find authors by ID in a specific column."""
    author_ids = set()
    for author_id in ids:
        try:
            author_row = authors_df[authors_df[column_name] == author_id]
            author_ids.add(author_row.index.values[0])
        except Exception as e:
            print(f"Error finding author by id: {str(e)}")
    return author_ids


def add_authors_by_names(session, authors_df, names, column_name, book):
    """Helper function to add authors by name to a book."""
    for name in names:
        try:
            author_rows = authors_df[authors_df[column_name].str.contains(name, case=False, na=False)]
            new_author = None
            if author_rows.empty:
                new_author = session.execute(select(Author).where(Author.name == name)).scalar()
                if not new_author:
                    new_author = Author(name=name)
                    session.add(new_author)
                    session.flush()
            else:
                new_author = process_author(session, author_rows.iloc[0])
            if new_author and new_author not in book.authors:
                book.authors.append(new_author)
        except Exception as e:
            print(f"Error finding author by name: {str(e)}")


def add_authors_by_indices(session, authors_df, indices, book):
    """Helper function to add authors by index to a book."""
    for index in indices:
        try:
            author_row = authors_df.loc[index, :]
            new_author = process_author(session, author_row)
            if new_author and new_author not in book.authors:
                book.authors.append(new_author)
        except Exception as e:
            print(f"Error finding author by index: {str(e)}")


def process_authors(session, book, book_row, authors_df):
    authors_found = False

    if not authors_found:
        authors_cdl = find_authors_by_id(authors_df, book_row['authors_id_cdl'], 'id_cdl')
        add_authors_by_indices(session, authors_df, authors_cdl, book)
        authors_found = True

    if not authors_found:
        authors_ol = find_authors_by_id(authors_df, book_row['authors_ol'], 'key_ol')
        add_authors_by_indices(session, authors_df, authors_ol, book)
        authors_found = True

    if not authors_found:
        author_names = set()
        if not pd.isna(book_row['autor_alejandria']):
            for author_name in re.split(r"\s[-Y/]\s|,", book_row['autor_alejandria']):
                author_names.add(author_name.strip())
        add_authors_by_names(session, authors_df, author_names, 'autor_nombre_alejandria', book)
        authors_found = True


def merge_books(book1, book2):
    """
    Merge book2 into book1 by filling in missing fields in book1 with those from book2.
    :param book1: The book to be updated (existing book in the database).
    :param book2: The book providing additional data (new book being processed).
    :return: The updated book1 with merged fields.
    """
    # Use SQLAlchemy inspection to get all column names
    mapper = inspect(book1.__class__)
    fields = [column.key for column in mapper.columns]

    for field in fields:
        if field == 'id':
            continue
        # Get the value from book1 and book2
        value1 = getattr(book1, field, None)
        value2 = getattr(book2, field, None)

        # If the field in book1 is None, update it with the value from book2
        if value1 is None and value2 is not None:
            setattr(book1, field, value2)

    return book1


def process_book(book_row):
    book_data = {
        'title': get_field_value(book_row, 'title', book_row['title_alejandria']),
        'isbn_10': get_field_value(book_row, 'isbn_10'),
        'isbn_13': get_field_value(book_row, 'isbn_13'),
        'publish_date': get_field_value(book_row, 'publish_date'),
        'description': get_field_value(book_row, 'description'),
        'cover_url': get_field_value(book_row, 'covers'),
        'current_price': get_field_value(book_row, 'current_price', 0),
        'previous_price': get_field_value(book_row, 'previous_price', 0),
        'price_alejandria': get_field_value(book_row, 'precio'),
        'iva': get_field_value(book_row, 'iva'),
        'cost': get_field_value(book_row, 'ultimo_costo'),
        'cost_supplier': get_field_value(book_row, 'costo_proveedor'),
        'average_cost_alejandria': get_field_value(book_row, 'costo_promedio'),
        'last_cost_alejandria': get_field_value(book_row, 'ultimo_costo'),
        'stock': get_field_value(book_row, 'stock_propio'),
        'stock_alejandria': get_field_value(book_row, 'stock_propio'),
        'stock_consig': get_field_value(book_row, 'stock_consig'),
        'stock_consig_alejandria': get_field_value(book_row, 'stock_consig'),
        'physical_format': get_field_value(book_row, 'physical_format'),
        'number_of_pages': get_field_value(book_row, 'number_of_pages'),
        'bar_code_alejandria': get_field_value(book_row, 'barra_cod'),
        'isbn_alejandria': get_field_value(book_row, 'isbn'),
        'code_alejandria': get_field_value(book_row, 'alejandria_id'),
        'physical_dimensions': get_field_value(book_row, 'physical_dimensions'),
        'weight': get_field_value(book_row, 'weight'),
        'publish_places': book_row['publish_places'],
        'edition_name': get_field_value(book_row, 'edition_name'),
        'subtitle': get_field_value(book_row, 'subtitle')
    }
    new_book_data = BookSchema().load(book_data)
    new_book = Book(**new_book_data)
    return new_book


def process_provider(session, provider_row):
    provider_data = {
        'id': provider_row['cod_proveedor'],
        'alejandria_code': provider_row['cod_proveedor'],
        'cedula': provider_row['cedula_proveedor'],
        'name': get_field_value(provider_row, 'nombre_proveedor'),
        'address': get_field_value(provider_row, 'direccion_proveedor'),
        'phone': get_field_value(provider_row, 'telefono_proveedor'),
        'email': get_field_value(provider_row, 'correo_proveedor'),
        'contact_name': get_field_value(provider_row, 'nombre_contacto_proveedor'),
        'nombre_banco': get_field_value(provider_row, 'nombre_banco_proveedor'),
        'titular_banco': get_field_value(provider_row, 'titular_banco_proveedor'),
        'rif_banco': get_field_value(provider_row, 'rif_banco_proveedor'),
        'cod_cuenta': get_field_value(provider_row, 'cuenta_banco_proveedor'),
        'notes': get_field_value(provider_row, 'notas')
    }
    provider_data = ProviderSchema().load(provider_data)
    provider = session.execute(select(Provider).where(Provider.id == provider_data['id'])).scalar()
    if not provider:
        provider = Provider(**provider_data)
        session.add(provider)
        session.flush()
    return provider


def process_providers(session, book, book_row, providers_df):
    provider_id = book_row['cod_proveedor']
    if pd.isna(provider_id) or provider_id is None:
        return
    try:
        provider_rows = providers_df[providers_df['cod_proveedor'] == provider_id]
        if provider_rows.empty:
            raise Exception(provider_id)
        provider_row = provider_rows.iloc[0]
        provider = process_provider(session, provider_row)
        if provider and provider not in book.providers:
            book.providers.append(provider)
    except Exception as e:
        print(f"Error finding provider with id: {str(e)}")


def process_genre(session, book, book_row):
    alejandria_genre = get_field_value(book_row, 'nom_tema')
    genres = book_row['genres']
    genres = set(genres)
    if alejandria_genre:
        genres.add(alejandria_genre)
    print(genres)
    for gen in genres:
        genre_data = GenreSchema().load({'name': gen.title()})
        genre = session.execute(select(Genre).where(Genre.name == genre_data['name'])).scalar()
        if not genre:
            genre = Genre(**genre_data)
            session.add(genre)
            session.flush()  # Ensure the genre gets an ID
        if genre not in book.genres:
            book.genres.append(genre)


def process_publishers(session, book, book_row):
    for pub in book_row['publishers']:
        publisher_data = PublisherSchema().load({'name': pub})
        publisher = session.execute(select(Publisher).where(Publisher.name == publisher_data['name'])).scalar()
        if not publisher:
            publisher = Publisher(**publisher_data)
            session.add(publisher)
            session.flush()
        if publisher not in book.publishers:
            book.publishers.append(publisher)


def process_languages(session, book, book_row):
    for lang in book_row['languages']:
        language_data = LanguageSchema().load({'name': lang})
        language = session.execute(select(Language).where(Language.name == language_data['name'])).scalar()
        if not language:
            language = Language(**language_data)
            session.add(language)
            session.flush()
        if language not in book.languages:
            book.languages.append(language)


def process_series(session, book, book_row):
    for ser in book_row['series']:
        series_data = SeriesSchema().load({'name': ser})
        series = session.execute(select(Series).where(Series.name == series_data['name'])).scalar()
        if not series:
            series = Series(**series_data)
            session.add(series)
            session.flush()
        if series not in book.series:
            book.series.append(series)


commit = True

# TODO: add some books to the featured books table


@api.cli.command(name='populate')
@click.option('--books_path', help='CSV file to read book data from')
@click.option('--authors_path', help='CSV file to read author data from')
@click.option('--providers_path', help='CSV file to read providers data from')
@click.option('--batch_size', help='Size of the batch to commit to the database', default=50)
@click.option('--limit', help='limit of books to add to the database', default=100)
@with_appcontext
def populate(books_path, authors_path, providers_path, batch_size, limit):
    logger = current_app.logger
    logger.info("Populating database with data from CSV files")
    logger.info("Books path: %s", books_path)
    logger.info("Authors path: %s", authors_path)
    logger.info("Providers path: %s", providers_path)
    books_df = pd.read_csv(books_path, dtype={'isbn_13': str, 'isbn_10': str, 'ean': str}, sep='\t')
    book_list_fields = ['languages', 'series', 'publish_places', 'subjects', 'authors_ol', 'authors_cdl', 'authors_id_cdl', 'genres', 'publishers']
    books_df = deserialize_columns(books_df, book_list_fields)
    authors_df = pd.read_csv(authors_path, dtype={'id_cdl': str}, sep='\t')
    authors_list_fields = ['id_alejandria', 'isbn_alejandria']
    authors_df = deserialize_columns(authors_df, authors_list_fields)
    provider_df = pd.read_csv(providers_path, sep='\t')
    session = db.session
    if limit:
        books_df = books_df.sample(limit)
    try:
        for index, row in books_df.iterrows():
            logger.info("Processing book %d", index)
            new_book = process_book(row)
            # Check if book already exists
            existing_book = session.execute(
                select(Book).where(
                    or_(
                        and_(
                            Book.code_alejandria == new_book.code_alejandria,
                            Book.title == new_book.title
                        ),
                        and_(
                            Book.isbn_10.is_not(None),
                            Book.isbn_10 == new_book.isbn_10
                        ),
                        and_(
                            Book.isbn_13.is_not(None),
                            Book.isbn_13 == new_book.isbn_13
                        )
                    )
                )
            ).scalar()

            if existing_book:
                logger.info("Book %s already exists", existing_book)
                logger.info("Attempting to merge book data.")
                logger.info("\tNew book: %s", new_book)
                logger.info("\tExisting book: %s", existing_book)
                new_book = merge_books(existing_book, new_book)
                logger.info("\tMerged book: %s", new_book)
            session.add(new_book)
            session.flush()
            logger.info("Book %s added", new_book)
            process_genre(session, new_book, row)
            logger.info("\tGenres: %s", new_book.genres)
            process_publishers(session, new_book, row)
            logger.info("\tPublishers: %s", new_book.publishers)
            process_languages(session, new_book, row)
            logger.info("\tLanguages: %s", new_book.languages)
            process_series(session, new_book, row)
            logger.info("\tSeries: %s", new_book.series)
            process_providers(session, new_book, row, provider_df)
            logger.info("\tProviders: %s", new_book.providers)
            process_authors(session, new_book, row, authors_df)
            logger.info("\tAuthors: %s", new_book.authors)
            if commit:
                if (index + 1) % batch_size == 0:
                    session.flush()  # Push changes to the database without committing
                    session.commit()  # Commit the batch
        if commit:
            session.commit()  # Final commit for remaining books
    except Exception as e:
        print(f"Error processing books: {str(e)}")
        if commit:
            session.rollback()
        raise e
    finally:
        session.close()
