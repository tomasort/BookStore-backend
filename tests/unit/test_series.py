import json


def test_create_series(client):
    # Create a new series
    response = client.post(
        '/api/series',
        data=json.dumps({'name': 'Harry Potter'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == 'Series created successfully'
    assert data['series_id'] == 1


def test_get_series(client):
    # Create new series
    series_ids = []
    for series in ['Harry Potter', 'The Hunger Games', 'Twilight']:
        response = client.post(
            '/api/series',
            data=json.dumps({'name': series}),
            content_type='application/json'
        )
        assert response.status_code == 201
        series_ids.append(json.loads(response.data)['series_id'])
    # Retrieve a list of series
    response = client.get('/api/series')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data) == 3
    assert all([series['id'] in series_ids for series in data])


def test_get_single_series(client):
    # Create new series
    series_ids = []
    for series in ['Harry Potter', 'The Hunger Games', 'Twilight']:
        response = client.post(
            '/api/series',
            data=json.dumps({'name': series}),
            content_type='application/json'
        )
        assert response.status_code == 201
        series_ids.append(json.loads(response.data)['series_id'])
    # Retrieve a single series by its ID
    response = client.get(f'/api/series/{series_ids[0]}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['id'] == series_ids[0]
    assert data['name'] == 'Harry Potter'
    # Test for a series that does not exist
    response = client.get('/api/series/999')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Series not found'


def test_update_series(client):
    # Create a new series
    response = client.post(
        '/api/series',
        data=json.dumps({'name': 'Harry Potter'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == 'Series created successfully'
    assert data['series_id'] == 1
    # Update the series
    response = client.put(
        '/api/series/1',
        data=json.dumps({'name': 'Harry Potter 2'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Series updated successfully'
    # Test for a series that does not exist
    response = client.put(
        '/api/series/999',
        data=json.dumps({'name': 'Harry Potter 2'}),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Series not found'


def test_delete_series(client):
    # Create a new series
    response = client.post(
        '/api/series',
        data=json.dumps({'name': 'Harry Potter'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == 'Series created successfully'
    assert data['series_id'] == 1
    # Delete the series
    response = client.delete('/api/series/1')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Series deleted successfully'
    # Test for a series that does not exist
    response = client.delete('/api/series/999')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Series not found'
