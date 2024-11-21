import json

def test_create_publisher(client):
    # Create a new publisher
    response = client.post(
        '/api/publishers',
        data=json.dumps({'name': 'Penguin Random House'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == 'Publisher created successfully'
    assert data['publisher_id'] == 1


def test_get_publishers(client):
    # Create new publishers
    publisher_ids = []
    for publisher in ['Penguin Random House', 'HarperCollins', 'Simon & Schuster']:
        response = client.post(
            '/api/publishers',
            data=json.dumps({'name': publisher}),
            content_type='application/json'
        )
        assert response.status_code == 201
        publisher_ids.append(json.loads(response.data)['publisher_id'])
    # Retrieve a list of publishers
    response = client.get('/api/publishers')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data) == 3
    assert all([publisher['id'] in publisher_ids for publisher in data])


def test_get_publisher(client):
    # Create new publishers
    publisher_ids = []
    for publisher in ['Penguin Random House', 'HarperCollins', 'Simon & Schuster']:
        response = client.post(
            '/api/publishers',
            data=json.dumps({'name': publisher}),
            content_type='application/json'
        )
        assert response.status_code == 201
        publisher_ids.append(json.loads(response.data)['publisher_id'])
    # Retrieve a single publisher by its ID
    response = client.get(f'/api/publishers/{publisher_ids[0]}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['id'] == publisher_ids[0]
    assert data['name'] == 'Penguin Random House'
    # Test for a publisher that does not exist
    response = client.get('/api/publishers/999')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Publisher not found'


def test_update_publisher(client):
    # Create a new publisher
    response = client.post(
        '/api/publishers',
        data=json.dumps({'name': 'Penguin Random House'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    publisher_id = json.loads(response.data)['publisher_id']
    # Update the publisher
    response = client.put(
        f'/api/publishers/{publisher_id}',
        data=json.dumps({'name': 'Penguin Classics'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Publisher updated successfully'
    # Retrieve the updated publisher
    response = client.get(f'/api/publishers/{publisher_id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['name'] == 'Penguin Classics'
    # Test for a publisher that does not exist
    response = client.put(
        '/api/publishers/999',
        data=json.dumps({'name': 'Penguin Classics'}),
        content_type='application/json'
    )
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Publisher not found'
    # Test for invalid publisher data
    response = client.put(
        f'/api/publishers/{publisher_id}',
        data=json.dumps({'invalid': 'data'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Invalid publisher data'

def test_delete_publisher(client):
    # Create a new publisher
    response = client.post(
        '/api/publishers',
        data=json.dumps({'name': 'Penguin Random House'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    publisher_id = json.loads(response.data)['publisher_id']
    # Delete the publisher
    response = client.delete(f'/api/publishers/{publisher_id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Publisher deleted successfully'
    # Test for a publisher that does not exist
    response = client.delete('/api/publishers/999')
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Publisher not found'
