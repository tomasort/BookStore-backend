import json


def test_create_genre(client):
    # Create a new genre
    response = client.post(
        '/api/genres',
        data=json.dumps({'name': 'Science Fiction'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == 'Genre created successfully'
    assert data['genre_id'] == 1


def test_get_genres(client):
    # Create new genres
    genre_ids = []
    for genre in ['Science Fiction', 'Fantasy', 'Mystery']:
        response = client.post(
            '/api/genres',
            data=json.dumps({'name': genre}),
            content_type='application/json'
        )
        assert response.status_code == 201
        genre_ids.append(json.loads(response.data)['genre_id'])
    # Retrieve a list of genres
    response = client.get('/api/genres')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data) == 3
    assert all([genre['id'] in genre_ids for genre in data])


def test_get_genre(client):
    # Create new genres
    genre_ids = []
    for genre in ['Science Fiction', 'Fantasy', 'Mystery']:
        response = client.post(
            '/api/genres',
            data=json.dumps({'name': genre}),
            content_type='application/json'
        )
        assert response.status_code == 201
        genre_ids.append(json.loads(response.data)['genre_id'])
    # Retrieve a single genre by its ID
    response = client.get(f'/api/genres/{genre_ids[0]}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['id'] == genre_ids[0]
    assert data['name'] == 'Science Fiction'
    # Test for a genre that does not exist
    response = client.get('/api/genres/999')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Genre not found'


def test_update_genre(client):
    # Create a new genre
    response = client.post(
        '/api/genres',
        data=json.dumps({'name': 'Science Fiction'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    genre_id = json.loads(response.data)['genre_id']
    # Update the genre
    response = client.put(
        f'/api/genres/{genre_id}',
        data=json.dumps({'name': 'Sci-Fi'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Genre updated successfully'
    # Retrieve the updated genre
    response = client.get(f'/api/genres/{genre_id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['name'] == 'Sci-Fi'
    # Test for a genre that does not exist
    response = client.put(
        '/api/genres/999',
        data=json.dumps({'name': 'Fantasy'}),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Genre not found'
    # Test for invalid genre data
    response = client.put(
        f'/api/genres/{genre_id}',
        data=json.dumps({'genre_name': 'Fantasy'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Invalid genre data'


def test_delete_genre(client):
    # Create a new genre
    response = client.post(
        '/api/genres',
        data=json.dumps({'name': 'Science Fiction'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    genre_id = json.loads(response.data)['genre_id']
    # Delete the genre
    response = client.delete(f'/api/genres/{genre_id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Genre deleted successfully'
    # Test for a genre that does not exist
    response = client.delete(f'/api/genres/{genre_id}')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Genre not found'
