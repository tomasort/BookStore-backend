import json


def test_create_simple_book(client, test_book_data):
    # Sample book data to create
    new_book_title = test_book_data['title']
    # Send a POST request to create a new book
    response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    # Assert that the request was successful
    print(response.get_json())
    assert response.status_code == 201
    response_data = response.get_json()
    assert "book_id" in response_data
    assert new_book_title in response_data['book_title']


def test_get_books(client, test_book_data):
    # add a book to the database
    response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    # Send a GET request to retrieve all books
    response = client.get("/api/books")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Should return a list of books
    assert len(data) > 0  # The list should not be empty
    assert data[0]["title"] == test_book_data["title"]


def test_get_specific_book(client, test_book_data):
    # add a book to the database
    create_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    print(create_response.get_json())
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book_id"]
    book_title = create_response.get_json()["book_title"]

    # Send a GET request to retrieve the specific book
    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    book = response.get_json()
    assert book["id"] == book_id
    assert book["title"] == book_title


def test_update_book(client, test_book_data):
    # Create a book to update
    create_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book_id"]

    # Update the book's title
    update_data = {"title": "Updated Test Book"}
    update_response = client.put(
        f"/api/books/{book_id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )

    print(update_response.get_json())
    # Assert that the update was successful
    assert update_response.status_code == 200

    # Retrieve the updated book to verify changes
    response = client.get(f"/api/books/{book_id}")
    book = response.get_json()
    assert book["title"] == "Updated Test Book"


def test_delete_book(client, test_book_data):
    # Create a book to delete
    create_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book_id"]

    options_response = client.options(f"/api/books/{book_id}")
    # This should include "DELETE"
    print(options_response.headers.get("Allow"))

    # Send a DELETE request to remove the book
    delete_response = client.delete(f"/api/books/{book_id}")
    print(delete_response.get_json())
    assert delete_response.status_code == 200

    # Verify that the book no longer exists
    get_response = client.get(f"/api/books/{book_id}")
    assert get_response.status_code == 404


def test_search_books_by_title(client, test_book_data):
    # Create a book to search for
    create_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    assert create_response.status_code == 201

    # Search by title
    search_response = client.get("/api/books/search?title=Test%20Book")
    assert search_response.status_code == 200

    # Verify the search results
    data = search_response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(book["title"] == test_book_data["title"] for book in data)


def test_search_books_by_isbn(client, test_book_data):
    # Create a book to search for
    create_response = client.post(
        "/api/books",
        data=json.dumps(test_book_data),
        content_type="application/json"
    )
    assert create_response.status_code == 201

    # Search by ISBN-10
    isbn_10 = test_book_data["isbn_10"]
    search_response = client.get(f"/api/books/search?isbn={isbn_10}")
    assert search_response.status_code == 200

    # Verify the search results
    data = search_response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(book["isbn_10"] == isbn_10 for book in data)


def test_search_books_no_results(client):
    # Search for a non-existing book
    search_response = client.get("/api/books/search?title=NonExistentTitle")
    assert search_response.status_code == 404

    # Verify the response contains an appropriate message
    data = search_response.get_json()
    assert "message" in data
    assert data["message"] == "No books found matching the search criteria"


# def test_search_books_by_author(client, test_book_data, test_author):
#     # Create an author and associate the book
#     create_author_response = client.post(
#         "/api/authors",
#         data=json.dumps(test_author),
#         content_type="application/json"
#     )
#     assert create_author_response.status_code == 201
#     author_id = create_author_response.get_json()["author_id"]

#     # Add the author ID to the book data and create the book
#     test_book_data["author_id"] = author_id
#     create_book_response = client.post(
#         "/api/books",
#         data=json.dumps(test_book_data),
#         content_type="application/json"
#     )
#     assert create_book_response.status_code == 201

#     # Search by author's name
#     author_name = test_author["name"]
#     search_response = client.get(f"/api/books/search?author={author_name}")
#     assert search_response.status_code == 200

#     # Verify the search results
#     data = search_response.get_json()
#     assert isinstance(data, list)
#     assert len(data) > 0
#     assert any(book["author_id"] == author_id for book in data)


# def test_combined_search_books(client, test_book_data, test_author):
#     # Create an author and associate the book
#     create_author_response = client.post(
#         "/api/authors",
#         data=json.dumps(test_author),
#         content_type="application/json"
#     )
#     assert create_author_response.status_code == 201
#     author_id = create_author_response.get_json()["author_id"]

#     # Add the author ID to the book data and create the book
#     test_book_data["author_id"] = author_id
#     create_book_response = client.post(
#         "/api/books",
#         data=json.dumps(test_book_data),
#         content_type="application/json"
#     )
#     assert create_book_response.status_code == 201

#     # Perform a combined search by title and author
#     search_response = client.get(
#         f"/api/books/search?title={test_book_data['title']}&author={test_author['name']}"
#     )
#     assert search_response.status_code == 200

#     # Verify the search results
#     data = search_response.get_json()
#     assert isinstance(data, list)
#     assert len(data) > 0
#     assert any(book["title"] == test_book_data["title"] and book["author_id"] == author_id for book in data)
