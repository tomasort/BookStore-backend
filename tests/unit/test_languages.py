import json
from sqlalchemy import select, func
from random import choice
import pytest
from app.models import Language
from app.schemas import LanguageSchema
from app import db

language_schema = LanguageSchema()


def test_create_language(client, language_factory):
    language = language_factory.build()
    response = client.post(
        "api/languages",
        data=json.dumps(language_schema.dump(language)),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Language created successfully'
    assert 'language_id' in data
    assert data['language_id'] == 1


@pytest.mark.parametrize("num_languages", [1, 3, 10, 20])
def test_get_languages(client, language_factory, num_languages):
    language_factory.create_batch(num_languages)
    num_languages_in_db = db.session.execute(select(func.count()).select_from(Language)).scalar()
    response = client.get("api/languages")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == num_languages_in_db


@pytest.mark.parametrize("num_languages", [1, 3, 10, 20])
def test_get_language(client, language_factory, num_languages):
    languages = language_factory.create_batch(num_languages)
    selected_language = choice(languages)
    response = client.get(f"api/languages/{selected_language.id}")
    assert response.status_code == 200
    assert response.get_json()['name'] == selected_language.name


@pytest.mark.parametrize("num_languages", [1, 3, 10])
def test_update_language(client, language_factory, num_languages):
    languages = language_factory.create_batch(num_languages)
    selected_language = choice(languages)
    updated_data = {"name": "JavaScript"}
    previous_name = selected_language.name
    response = client.put(
        f"api/languages/{selected_language.id}",
        data=json.dumps({"name": "JavaScript"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Language updated successfully"
    assert previous_name != selected_language.name
    assert selected_language.name == updated_data["name"]


@pytest.mark.parametrize("num_languages", [1, 3, 10])
def test_delete_language(client, language_factory, num_languages):
    languages = language_factory.create_batch(num_languages)
    language_to_delete = choice(languages)
    response = client.delete(f"api/languages/{language_to_delete.id}")
    assert response.status_code == 200
    assert db.session.execute(select(Language).where(
        Language.id == language_to_delete.id)).scalar() is None
