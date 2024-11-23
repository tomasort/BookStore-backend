# Script for populating the database with the data from the csv
import click
import pandas as pd
from flask.cli import with_appcontext
from app import db
from app.api.models import Book, Author, Genre, Series
from app.api import api


@api.cli.command(name='populate')
@click.option('--path', help='CSV file to read data from')
@with_appcontext
def populate(path):
    # Read the csv file
    books_df = pd.DataFrame()
    try:
        books_df = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading the file: {str(e)}")
        return
    print(books_df.head())
