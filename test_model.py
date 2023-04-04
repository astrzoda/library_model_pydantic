import pytest
from fastapi.testclient import TestClient

from model import app


@pytest.fixture()
def api():
    return TestClient(app)


def test_create_user_can_be_retrieved(api):
    resp = api.post("/users/", json={"first_name": "Alice", "second_name": "Doe", "personal_id_nbr": "95032708202"})

    assert resp.status_code == 200

    pid = resp.json()["user_id"]
    resp = api.get(f"/users/{pid}")

    assert resp.status_code == 200
    user = resp.json()

    assert user["first_name"] == "Alice"
    assert user["second_name"] == "Doe"


def test_non_existing_user_cannot_be_retrieved(api):
    resp = api.get(f"/users/1050")
    assert resp.status_code == 404


def test_non_existing_book_cannot_be_retrieved(api):
    resp = api.get(f"/books/1050")
    assert resp.status_code == 404


def test_non_existing_user_cannot_rent_a_book(api):
    resp = api.post("/books/", json={"title": "XXX", "author": "YYY", "genre": "non-fiction",
                                     "age_rating": 0})

    assert resp.status_code == 200

    book_id = resp.json()["book_id"]
    resp = api.get(f"/books/{book_id}")

    assert resp.status_code == 200

    resp = api.post("/rentals/", json={"user_id": 1050, "rented_books_ids": [
        book_id
    ], "date": "2023-04-04T12:22:00.946Z"})

    assert resp.status_code == 404