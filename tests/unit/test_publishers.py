import json
from app.models import Publisher
from app.schemas import PublisherSchema
from sqlalchemy import select, func
from app import db
from random import choice
import pytest

publisher_schema = PublisherSchema()


def test_create_publisher(client, publisher_factory):
    # Create a new publisher
    publisher = publisher_factory.build()
    response = client.post(
        '/api/publishers',
        data=json.dumps(publisher_schema.dump(publisher)),
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
    num_publishers_in_db = db.session.execute(select(func.count()).select_from(Publisher)).scalar()
    # Retrieve a list of publishers
    response = client.get('/api/publishers')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == num_publishers_in_db
    created_publishers = {publisher.name for publisher in publishers}
    response_publishers = {publisher['name'] for publisher in data}
    assert created_publishers.issubset(response_publishers)


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
    num_publishers_in_db = db.session.execute(select(func.count()).select_from(Publisher)).scalar()
    target_publisher = choice(publishers)
    # Delete the publisher
    response = client.delete(f'/api/publishers/{target_publisher.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Publisher deleted successfully'
    assert db.session.execute(select(Publisher).where(Publisher.id == target_publisher.id)).scalar() is None
    assert db.session.execute(select(func.count()).select_from(Publisher)).scalar() == num_publishers_in_db - 1
