import json


def test_create_author(client, test_authors_data):
    # Test creating a new author
    response = client.post(
        "/api/authors",
        data=json.dumps(test_authors_data[0]),
        content_type="application/json"
    )
    print(response.get_json())
    assert response.status_code == 201
    data = response.get_json()
    assert "author_id" in data
    assert data["message"] == "Author created successfully"


def test_add_authors_to_book(client, test_book_data, test_authors_data):
    # Create a book to which authors will be added
    create_book_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    assert create_book_response.status_code == 201
    book_id = create_book_response.get_json()["book_id"]
    # Create two authors
    author_ids = []
    for author in test_authors_data:
        create_author_response = client.post(
            "/api/authors",
            data=json.dumps(author),
            content_type="application/json"
        )
        author_ids.append(create_author_response.get_json()["author_id"])
        assert create_author_response.status_code == 201
    # Send a POST request to add authors to the book
    add_authors_response = client.post(
        f"/api/books/{book_id}/authors",
        data=json.dumps({"author_ids": author_ids}),
        content_type="application/json"
    )
    # Verify that the response is successful
    print(add_authors_response.get_json())
    assert add_authors_response.status_code == 200
    data = add_authors_response.get_json()
    assert data["message"] == "Authors added successfully"

    # Verify that the authors were correctly added to the book
    get_book_response = client.get(f"/api/books/{book_id}")
    assert get_book_response.status_code == 200
    book_data = get_book_response.get_json()

    # Check that the authors were added
    new_author_ids = [author["id"] for author in book_data.get("authors", [])]
    for author_id in author_ids:
        assert author_id in new_author_ids


def test_get_authors(client, test_authors_data):
    # Add authors to the database
    author_ids = []
    for author in test_authors_data:
        response = client.post(
            "/api/authors",
            data=json.dumps(author),
            content_type="application/json"
        )
        assert response.status_code == 201
        author_ids.append(response.get_json()["author_id"])
    # Send a GET request to retrieve all authors
    response = client.get("/api/authors")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Should return a list of authors
    assert len(data) > 0  # The list should not be empty
    assert data[0]["name"] == test_authors_data[0]["name"]
    # check that the author ids are in the response
    for author in data:
        assert all([author['id'] in author_ids for author in data])


def test_get_author(client, test_authors_data):
    # Add an author to the database
    response = client.post(
        "/api/authors",
        data=json.dumps(test_authors_data[0]),
        content_type="application/json"
    )
    assert response.status_code == 201
    author_id = response.get_json()["author_id"]
    # Send a GET request to retrieve the author
    response = client.get(f"/api/authors/{author_id}")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == test_authors_data[0]["name"]
    # Check that the author id is in the response
    assert data["id"] == author_id
