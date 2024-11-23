import json
from app.api.models import Publisher
from sqlalchemy import select, func
from app import db
from random import choice
import pytest


def test_create_publisher(client, publisher_factory):
    # Create a new publisher
    publisher = publisher_factory.build()
    response = client.post(
        '/api/publishers',
        data=json.dumps(publisher.to_dict()),
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 201
    assert data['message'] == 'Publisher created successfully'
    assert data['publisher_id'] == 1


@pytest.mark.parametrize("num_publishers", [1, 3, 10, 20])
def test_get_publishers(client, publisher_factory, num_publishers):
    # Create new publishers
    publishers = publisher_factory.create_batch(num_publishers)
    # Retrieve a list of publishers
    response = client.get('/api/publishers')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == num_publishers
    publisher_ids = [publisher.id for publisher in publishers]
    assert all([publisher['id'] in publisher_ids for publisher in data])


@pytest.mark.parametrize("num_publishers", [1, 3, 10, 20])
def test_get_publisher(client, publisher_factory, num_publishers):
    publishers = publisher_factory.create_batch(num_publishers)
    target_publisher = choice(publishers)
    # Retrieve a single publisher by its ID
    response = client.get(f'/api/publishers/{target_publisher.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['id'] == target_publisher.id
    assert data['name'] == target_publisher.name


@pytest.mark.parametrize("num_publishers", [1, 3, 10])
def test_update_publisher(client, publisher_factory, num_publishers):
    publishers = publisher_factory.create_batch(num_publishers)
    target_publisher = choice(publishers)
    update_data = {'name': 'Changed Classics'}
    # Update the publisher
    response = client.put(
        f'/api/publishers/{target_publisher.id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Publisher updated successfully'
    assert target_publisher.name == update_data['name']


@pytest.mark.parametrize("num_publishers", [1, 3, 10])
def test_delete_publisher(client, publisher_factory, num_publishers):
    publishers = publisher_factory.create_batch(num_publishers)
    target_publisher = choice(publishers)
    # Delete the publisher
    response = client.delete(f'/api/publishers/{target_publisher.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Publisher deleted successfully'
    assert db.session.execute(select(Publisher).where(
        Publisher.id == target_publisher.id)).scalar() is None
    assert db.session.execute(select(func.count()).select_from(
        Publisher)).scalar() == num_publishers - 1
