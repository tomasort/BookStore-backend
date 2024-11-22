import json
from random import choice
import pytest
from app import db
from app.api.models import Genre
from sqlalchemy import select, func


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_create_genre(client, genre_factory, num_genres):
    genres = genre_factory.build_batch(num_genres)
    assert db.session.execute(
        select(func.count()).select_from(Genre)).scalar() == 0
    # Create a new genre
    for genre in genres:
        response = client.post(
            '/api/genres',
            data=json.dumps(genre.to_dict()),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 201
        assert data['message'] == 'Genre created successfully'
    # Verify that all the genres were created
    assert db.session.execute(
        select(func.count()).select_from(Genre)).scalar() == num_genres


@pytest.mark.parametrize("num_genres", [1, 3, 10, 20])
def test_get_genres(client, genre_factory, num_genres):
    genres = genre_factory.create_batch(num_genres)
    # Retrieve a list of genres
    response = client.get('/api/genres')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == num_genres
    genre_ids = [genre.id for genre in genres]
    assert all([genre['id'] in genre_ids for genre in data])


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
    # Delete the genre
    response = client.delete(f'/api/genres/{selected_genre.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Genre deleted successfully'
    assert db.session.execute(
        select(func.count()).select_from(Genre)).scalar() == num_genres - 1
    assert db.session.execute(select(Genre).where(
        Genre.id == selected_genre.id)).scalar() is None
