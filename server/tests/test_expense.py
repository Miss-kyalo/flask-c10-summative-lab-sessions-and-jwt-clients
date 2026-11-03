
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

import pytest
from werkzeug.security import generate_password_hash

from app import app
from models import db, User


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key"
    )

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        user1 = User(
            username="test_user_1",
            email="test1@example.com",
            password_hash=generate_password_hash("password123")
        )

        user2 = User(
            username="test_user_2",
            email="test2@example.com",
            password_hash=generate_password_hash("password123")
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        user1_id = user1.id

    # Create independent clients without nested context managers
    test_client1 = app.test_client()
    test_client2 = app.test_client()

    login1 = test_client1.post(
        "/login",
        json={
            "email": "test1@example.com",
            "password": "password123"
        }
    )

    login2 = test_client2.post(
        "/login",
        json={
            "email": "test2@example.com",
            "password": "password123"
        }
    )

    assert login1.status_code == 200
    assert login2.status_code == 200

    yield test_client1, test_client2, user1_id

    with app.app_context():
        db.session.remove()
        db.drop_all()


def create_test_expense(client):
    return client.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": 500,
            "category": "Food",
            "date": "2026-11-01"
        }
    )


def test_unauthenticated_user_cannot_access_expenses(client):
    with app.test_client() as unauthenticated_client:
        response = unauthenticated_client.get("/expenses")

    assert response.status_code == 401


def test_create_expense(client):
    test_client1, test_client2, user1_id = client

    response = create_test_expense(test_client1)

    assert response.status_code == 201
    assert response.get_json()["description"] == "Lunch"
    assert response.get_json()["user_id"] == user1_id


def test_get_expenses(client):
    test_client1, test_client2, user1_id = client

    create_test_expense(test_client1)

    response = test_client1.get("/expenses")

    assert response.status_code == 200
    assert len(response.get_json()["items"]) == 1


def test_update_expense(client):
    test_client1, test_client2, user1_id = client

    create_response = create_test_expense(test_client1)
    expense_id = create_response.get_json()["id"]

    response = test_client1.patch(
        f"/expenses/{expense_id}",
        json={"amount": 750}
    )

    assert response.status_code == 200
    assert float(response.get_json()["amount"]) == 750.0


def test_delete_expense(client):
    test_client1, test_client2, user1_id = client

    create_response = create_test_expense(test_client1)
    expense_id = create_response.get_json()["id"]

    response = test_client1.delete(
        f"/expenses/{expense_id}"
    )

    assert response.status_code == 200

    get_response = test_client1.get(
        f"/expenses/{expense_id}"
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_expense(client):
    test_client1, test_client2, user1_id = client

    create_response = create_test_expense(test_client1)
    expense_id = create_response.get_json()["id"]

    response = test_client2.get(
        f"/expenses/{expense_id}"
    )

    assert response.status_code == 404


def test_create_expense_with_invalid_amount(client):
    test_client1, test_client2, user1_id = client

    response = test_client1.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": -500,
            "category": "Food",
            "date": "2026-11-01"
        }
    )

    assert response.status_code == 400


def test_create_expense_with_missing_fields(client):
    test_client1, test_client2, user1_id = client

    response = test_client1.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": 500
        }
    )

    assert response.status_code == 400


def test_user_cannot_delete_another_users_expense(client):
    test_client1, test_client2, user1_id = client

    create_response = create_test_expense(test_client1)
    expense_id = create_response.get_json()["id"]

    response = test_client2.delete(
        f"/expenses/{expense_id}"
    )

    assert response.status_code == 404
