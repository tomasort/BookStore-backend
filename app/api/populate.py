# Script for populating the database with the data from the csv
from time import sleep
from sqlalchemy import select
from datetime import datetime
import click
import pandas as pd
from flask.cli import with_appcontext
from app import db
from app.api.models import Book, Author, Genre, Series
from app.api import api
from typing import List
import json


def deserialize_columns(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    result_df = df.copy()
    for column_name in column_names:
        result_df[column_name] = result_df[column_name].apply(json.loads)
    return result_df


@api.cli.command(name='populate')
@click.option('--books_path', help='CSV file to read book data from')
@click.option('--authors_path', help='CSV file to read author data from')
@with_appcontext
def populate(books_path, authors_path):
    # Read the csv file
    try:
        books_df = pd.read_csv(books_path, sep='\t')
        books_df = deserialize_columns(books_df, ['languages', 'publishers', 'series', 'publish_places', 'subjects', 'authors_ol', 'authors_cdl', 'authors_id_cdl', 'genres'])
        authors_df = pd.read_csv(authors_path, dtype={'id_cdl': str}, sep='\t')
        authors_df = deserialize_columns(authors_df, ['id_alejandria'])
        print(authors_df.info())

        for index, row in books_df.iterrows():
            print(row.get(cost))
            # book_data = {
            #     'title': row['title'],
            #     'isbn_10': row['isbn_10'],
            #     'isbn_13': row['isbn_13'],
            #     'publish_date': row['publish_date'],
            #     'description': row['description'],
            #     'cover_url': row['covers'],  # Mapping 'covers' to 'cover_url'
            #     'current_price': row['current_price'],
            #     'previous_price': row['previous_price'],
            #     'cost': row.get('cost'),  # Assuming the DataFrame has this field, or use None
            #     'cost_supplier': row.get('cost_supplier'),  # Same as above
            #     'physical_format': row['physical_format'],
            #     'number_of_pages': row['number_of_pages'],
            #     'editorial': row['editorial_alejandria'],  # Using 'editorial_alejandria' for 'editorial'
            #     'alejandria_isbn': row['alejandria_id'],  # Mapping 'alejandria_id' to 'alejandria_isbn'
            #     'publisher_id': None,  # Assuming publisher ID is managed elsewhere
            #     'physical_dimensions': row['physical_dimensions'],
            #     'weight': row['weight'],
            #     'publish_place': row['publish_places'][0] if isinstance(row['publish_places'], list) else row['publish_places'],
            #     'edition_name': row['edition_name'],
            #     'subtitle': row['subtitle'],
            #     # Relationships should be processed separately, likely with additional lookups or queries:
            #     'authors': [],  # Placeholder for author relationships
            #     'genres': [],   # Placeholder for genre relationships
            #     'publisher': None,  # Placeholder for publisher relationship
            #     'languages': [],  # Placeholder for language relationships
            #     'series': []  # Placeholder for series relationships
            # }
            # author_name_alejandria = row['autor_alejandria']
            # authors_cdl = authors_df[authors_df['id_cdl'].isin(row['authors_id_cdl'])]
            # authors_ol = authors_df[authors_df['key_ol'].isin(row['authors_ol'])]
            # if not pd.isna(author_name_alejandria):
            #     authors_name = authors_df[(authors_df['autor_nombre_alejandria'].isin(row['authors_cdl'])) | (authors_df['autor_nombre_alejandria'].str.contains(author_name_alejandria, case=False))]
            # print(authors_cdl)
            # print(authors_ol)
            # print(authors_name)
            break

        for index, row in authors_df.iterrows():
            print(row)
            break

    except Exception as e:
        print(f"Error reading the file: {str(e)}")
        raise e
        return


# @api.cli.command(name='provider')
# @click.option('--providers_path', help='CSV file to read provider data from')
# @click.option('--add_provider', help='Add a provider to the database')
# @with_appcontext
# def populate(books_path, authors_path):
#     # Read the csv file
#     try:
#         books_df = pd.read_csv(books_path, sep='\t')
#         books_df = deserialize_columns(books_df, ['languages', 'publishers', 'series', 'publish_places', 'subjects', 'authors_ol', 'authors_cdl', 'authors_id_cdl', 'genres'])
#         authors_df = pd.read_csv(authors_path, dtype={'id_cdl': str}, sep='\t')
#         authors_df = deserialize_columns(authors_df, ['id_alejandria'])
