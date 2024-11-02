import mysql.connector
import pandas as pd
import json

art_df = pd.read_csv('articulos.csv')
art_df['isbn_len'] = art_df['isbn'].apply(lambda x: len(str(x)))

resutl_df = pd.DataFrame()


for chunk in pd.read_csv('/mnt/datadrive/OpenLibrary/ol_cdump_2024-08-31/ol_cdump_2024-08-31.txt', header=None, sep='\t', chunksize=1000000):
    # Parse JSON objects in column 4
    json_column = chunk[4].apply(lambda x: json.loads(x))
    chunk['isbn10'] = json_column.apply(lambda obj: obj.get('isbn_10'))
    chunk['isbn13'] = json_column.apply(lambda obj: obj.get('isbn_13'))
    art_isbns = set(art_df['isbn'])
    chunk['present_10'] = chunk['isbn10'].apply(lambda x: any([isbn in art_isbns for isbn in x]) if x is not None else False)
    chunk['present_13'] = chunk['isbn13'].apply(lambda x: any([isbn in art_isbns for isbn in x]) if x is not None else False)
    chunk['title'] = json_column.apply(lambda obj: obj.get('title'))
    result = chunk[(chunk['present_10']) | (chunk['present_13'])][['title']]
    if result.shape[0] > 0:
        print(result)

    # Extract author information
    # chunk['type'] = chunk[0].str.split('/').str[2]
    # chunk['name'] = json_column.apply(lambda obj: obj.get('name'))
    # chunk['key'] = json_column.apply(lambda obj: obj.get('key'))
    # chunk['bio'] = json_column.apply(lambda obj: obj.get('bio'))
    # chunk['birth_date'] = json_column.apply(lambda obj: obj.get('birth_date'))
    # chunk['death_date'] = json_column.apply(lambda obj: obj.get('death_date'))

    # Extract book information
    # chunk['subtitle'] = json_column.apply(lambda obj: obj.get('subtitle'))
    # chunk['authors'] = json_column.apply(lambda obj: obj.get('authors'))
    # chunk['languages'] = json_column.apply(lambda obj: obj.get('languages'))
    # chunk['number_of_pages'] = json_column.apply(lambda obj: obj.get('number_of_pages'))
    # chunk['physical_dimensions'] = json_column.apply(lambda obj: obj.get('physical_dimensions'))
    # chunk['publish_country'] = json_column.apply(lambda obj: obj.get('physical_dimensions'))
    # chunk['publish_date'] = json_column.apply(lambda obj: obj.get('publish_date'))
    # chunk['genres'] = json_column.apply(lambda obj: obj.get('genres'))
    # chunk['other_titles'] = json_column.apply(lambda obj: obj.get('other_titles'))
    # chunk['description'] = json_column.apply(lambda obj: obj.get('description'))

    # print(chunk[['type', 'title', 'isbn10', 'isbn13', 'languages', 'description']][(chunk['type'] == 'edition') & (chunk['description'].notnull())])
    # print(chunk['isbn10'].apply(lambda x: len(x) if x is not None else 0).value_counts())
    # print(chunk['present'].value_counts())
    

def get_articulos():
    # MySQL database connection parameters
    host = 'localhost'  # e.g., 'localhost' or your database server IP
    user = 'root'
    password = 'odroid'
    database = 'alejandria'
    table_name = 'articulos'

    # Initialize connection variable
    connection = None

    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        # Check if the connection was successful
        if connection.is_connected():
            # Query to fetch all records from the table
            query = f"SELECT * FROM {table_name}"
            
            # Load data into a pandas DataFrame
            df = pd.read_sql(query, connection)
            
            print("Data fetched successfully!")
            df = df[['cod_art', 'nom_art', 'isbn', 'autor', 'cod_edito', 'cod_colecc', 'cod_tema', 'precio_1']]
            df.to_csv('articulos.csv', index=False)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Check if the connection was created and is still open before closing it
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

