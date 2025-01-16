import json
from random import choice
import pytest
from app import db
from app.models import Genre
from app.schemas import GenreSchema
from sqlalchemy import select, func

genre_schema = GenreSchema()


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_create_genre(client, genre_factory, num_genres):
    genres = genre_factory.build_batch(num_genres)
    # Create a new genre
    for genre in genres:
        response = client.post(
            '/api/genres',
            data=json.dumps(genre_schema.dump(genre)),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 201
        assert data['message'] == 'Genre created successfully'
    created_genres = {genre.name for genre in genres}
    genres_in_db = set(db.session.execute(select(Genre.name)).scalars())
    assert created_genres.issubset(genres_in_db)


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_get_genres(client, genre_factory, num_genres):
    num_genres_in_db = db.session.execute(select(func.count()).select_from(Genre)).scalar()
    genres = genre_factory.create_batch(num_genres)
    # Retrieve a list of genres
    response = client.get('/api/genres')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == num_genres_in_db + num_genres
    created_genres = {genre.name for genre in genres}
    response_genres = {genre['name'] for genre in data}
    assert created_genres.issubset(response_genres)


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_get_genre(client, genre_factory, num_genres):
    genres = genre_factory.create_batch(num_genres)
    selected_genre = choice(genres)
    # Retrieve a single genre by its ID
    response = client.get(f'/api/genres/{selected_genre.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['id'] == selected_genre.id
    assert data['name'] == selected_genre.name


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_update_genre(client, genre_factory, num_genres):
    genres = genre_factory.create_batch(num_genres)
    selected_genre = choice(genres)
    # Update the genre
    updated_data = {'name': 'Changed Genre'}
    response = client.put(
        f'/api/genres/{selected_genre.id}',
        data=json.dumps(updated_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Genre updated successfully'
    assert selected_genre.name == updated_data['name']


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_delete_genre(client, genre_factory, num_genres):
    genres = genre_factory.create_batch(num_genres)
    selected_genre = choice(genres)
    num_genres_in_db = db.session.execute(select(func.count()).select_from(Genre)).scalar()
    # Delete the genre
    response = client.delete(f'/api/genres/{selected_genre.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Genre deleted successfully'
    assert db.session.execute(select(func.count()).select_from(Genre)).scalar() == num_genres_in_db - 1
    assert db.session.execute(select(Genre).where(Genre.id == selected_genre.id)).scalar() is None
