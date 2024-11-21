import json

def test_create_language(client):
    response = client.post(
        "api/languages",
        data=json.dumps({"name": "Python"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json == {"language_id": 1, "message": "Language created successfully"}

def test_get_languages(client):
    response = client.get("api/languages")
    assert response.status_code == 200
    assert response.json == []
    language = {"id": 1, "name": "Python"}
    client.post("api/languages", data=json.dumps(language), content_type="application/json")
    response = client.get("api/languages")
    assert response.status_code == 200
    assert response.json == [language]

def test_get_language(client):
    response = client.get("api/languages/1")
    assert response.status_code == 404
    language = {"id": 1, "name": "Python"}
    client.post("api/languages", data=json.dumps(language), content_type="application/json")
    response = client.get("api/languages/1")
    assert response.status_code == 200
    assert response.json == language

def test_update_language(client):
    response = client.put(
        "api/languages/1",
        data=json.dumps({"name": "Python"}),
        content_type="application/json",
    )
    assert response.status_code == 404
    language = {"id": 1, "name": "Python"}
    client.post("api/languages", data=json.dumps(language), content_type="application/json")
    response = client.put(
        "api/languages/1",
        data=json.dumps({"name": "JavaScript"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json == {"message": "Language updated successfully"}
    response = client.get("api/languages/1")
    assert response.status_code == 200
    assert response.json == {"id": 1, "name": "JavaScript"}

def test_delete_language(client):
    response = client.delete("api/languages/1")
    assert response.status_code == 404
    language = {"id": 1, "name": "Python"}
    client.post("api/languages", data=json.dumps(language), content_type="application/json")
    response = client.delete("api/languages/1")
    assert response.status_code == 200
    response = client.get("api/languages/1")
    assert response.status_code == 404
