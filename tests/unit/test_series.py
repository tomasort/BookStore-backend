import json
import pytest
from app import db
from random import choice
from urllib.parse import quote
from app.api.models import Series
from sqlalchemy import select, func


@pytest.mark.parametrize("num_series", [1, 3, 10, 20])
def test_create_series(client, series_factory, num_series):
    series_in_db = db.session.execute(select(func.count()).select_from(Series)).scalar()
    series = series_factory.build_batch(num_series)
    for s in series:
        # Create a new series
        response = client.post(
            '/api/series',
            data=json.dumps(s.to_dict()),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 201
        assert data['message'] == 'Series created successfully'
    # Verify that all the series were created
    assert db.session.execute(select(func.count()).select_from(Series)).scalar() == series_in_db + num_series


@pytest.mark.parametrize("num_series", [1, 3, 10, 20])
def test_get_series(client, series_factory, num_series):
    # Create new series
    series = series_factory.create_batch(num_series)
    num_series_in_db = db.session.execute(select(func.count()).select_from(Series)).scalar()
    # Retrieve a list of series
    response = client.get('/api/series')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == num_series_in_db
    created_series = {s.name for s in series}
    response_series = {s['name'] for s in data}
    assert created_series.issubset(response_series)


@pytest.mark.parametrize("num_series", [1, 3, 10, 20])
def test_get_single_series(client, series_factory, num_series):
    # Create new series
    series = series_factory.create_batch(num_series)
    selected_series = choice(series)
    # Retrieve a single series by its ID
    response = client.get(f'/api/series/{selected_series.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['id'] == selected_series.id
    assert data['name'] == selected_series.name


@pytest.mark.parametrize("num_series", [1, 3, 10])
def test_update_series(client, series_factory, num_series):
    # Create new series
    series = series_factory.create_batch(num_series)
    selected_series = choice(series)
    # Update the series
    updated_data = {'name': 'Changed Series'}
    response = client.put(
        f'/api/series/{selected_series.id}',
        data=json.dumps(updated_data),
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Series updated successfully'
    assert selected_series.name == updated_data['name']


@pytest.mark.parametrize("num_series", [1, 10])
def test_delete_series(client, series_factory, num_series):
    # Create a new series
    series = series_factory.create_batch(num_series)
    num_series_in_db = db.session.execute(select(func.count()).select_from(Series)).scalar()
    selected_series = choice(series)
    # Delete the series
    response = client.delete(f'/api/series/{selected_series.id}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Series deleted successfully'
    assert db.session.execute(select(func.count()).select_from(Series)).scalar() == num_series_in_db - 1
    assert db.session.execute(select(Series).where(Series.id == selected_series.id)).scalar() is None
