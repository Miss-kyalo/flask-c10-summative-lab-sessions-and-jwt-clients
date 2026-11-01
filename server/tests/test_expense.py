
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

import pytest
from flask_jwt_extended import create_access_token

from app import app
from models import db, User


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret-key"
    )

    with app.app_context():
        db.create_all()

        user1 = User(
            username="test_user_1",
            password_hash="temporary"
        )
        user2 = User(
            username="test_user_2",
            password_hash="temporary"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        token1 = create_access_token(identity=str(user1.id))
        token2 = create_access_token(identity=str(user2.id))

    with app.test_client() as test_client:
        yield test_client, token1, token2

    with app.app_context():
        db.session.remove()
        db.drop_all()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_test_expense(client, token):
    return client.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": 500,
            "category": "Food",
            "date": "2026-11-01"
        },
        headers=auth_headers(token)
    )


def test_unauthenticated_user_cannot_access_expenses(client):
    test_client, token1, token2 = client

    response = test_client.get("/expenses")

    assert response.status_code == 401


def test_create_expense(client):
    test_client, token1, token2 = client

    response = create_test_expense(test_client, token1)

    assert response.status_code == 201
    assert response.get_json()["description"] == "Lunch"
    assert response.get_json()["user_id"] == 1


def test_get_expenses(client):
    test_client, token1, token2 = client

    create_test_expense(test_client, token1)

    response = test_client.get(
        "/expenses",
        headers=auth_headers(token1)
    )

    assert response.status_code == 200
    assert len(response.get_json()["expenses"]) == 1


def test_update_expense(client):
    test_client, token1, token2 = client

    create_response = create_test_expense(test_client, token1)
    expense_id = create_response.get_json()["id"]

    response = test_client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 750},
        headers=auth_headers(token1)
    )

    assert response.status_code == 200
    assert response.get_json()["amount"] == "750.00"


def test_delete_expense(client):
    test_client, token1, token2 = client

    create_response = create_test_expense(test_client, token1)
    expense_id = create_response.get_json()["id"]

    response = test_client.delete(
        f"/expenses/{expense_id}",
        headers=auth_headers(token1)
    )

    assert response.status_code == 200

    get_response = test_client.get(
        f"/expenses/{expense_id}",
        headers=auth_headers(token1)
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_expense(client):
    test_client, token1, token2 = client

    create_response = create_test_expense(test_client, token1)
    expense_id = create_response.get_json()["id"]

    response = test_client.get(
        f"/expenses/{expense_id}",
        headers=auth_headers(token2)
    )

    assert response.status_code == 404


def test_create_expense_with_invalid_amount(client):
    test_client, token1, token2 = client

    response = test_client.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": -500,
            "category": "Food",
            "date": "2026-11-01"
        },
        headers=auth_headers(token1)
    )

    assert response.status_code == 400


def test_create_expense_with_missing_fields(client):
    test_client, token1, token2 = client

    response = test_client.post(
        "/expenses",
        json={
            "description": "Lunch",
            "amount": 500
        },
        headers=auth_headers(token1)
    )

    assert response.status_code == 400


def test_user_cannot_delete_another_users_expense(client):
    test_client, token1, token2 = client

    create_response = create_test_expense(test_client, token1)
    expense_id = create_response.get_json()["id"]

    response = test_client.delete(
        f"/expenses/{expense_id}",
        headers=auth_headers(token2)
    )

    assert response.status_code == 404
