import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

import pytest

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
        db.create_all()

        user1 = User(
            username="test_user_1",
            email="test1@example.com"
        )
        user1.password_hash = "temporary123"

        user2 = User(
            username="test_user_2",
            email="test2@example.com"
        )
        user2.password_hash = "temporary123"

        db.session.add_all([user1, user2])
        db.session.commit()

        user1_id = user1.id
        user2_id = user2.id

    with app.test_client() as test_client:
        yield test_client, user1_id, user2_id

    with app.app_context():
        db.session.remove()
        db.drop_all()


def login_as(test_client, user_id):
    with test_client.session_transaction() as session:
        session["user_id"] = user_id


def create_test_expense(test_client, user_id):
    login_as(test_client, user_id)

    return test_client.post(
        "/expenses",
        json={
            "title": "Lunch",
            "amount": 500,
            "category": "Food",
            "timestamp": "2026-11-01T12:00:00"
        }
    )


def test_unauthenticated_user_cannot_access_expenses(client):
    test_client, user1_id, user2_id = client
    response = test_client.get("/expenses")
    assert response.status_code == 401


def test_stale_session_cannot_create_expense(client):
    test_client, user1_id, user2_id = client
    login_as(test_client, 99999)

    response = test_client.post(
        "/expenses",
        json={
            "title": "Orphan",
            "amount": 10,
            "category": "Other"
        }
    )

    assert response.status_code == 401


def test_create_expense(client):
    test_client, user1_id, user2_id = client
    response = create_test_expense(test_client, user1_id)
    assert response.status_code == 201
    assert response.get_json()["title"] == "Lunch"
    assert response.get_json()["user_id"] == user1_id


def test_get_expenses(client):
    test_client, user1_id, user2_id = client
    create_test_expense(test_client, user1_id)
    login_as(test_client, user1_id)
    response = test_client.get("/expenses")
    assert response.status_code == 200
    assert len(response.get_json()["items"]) == 1


def test_update_expense(client):
    test_client, user1_id, user2_id = client
    create_response = create_test_expense(test_client, user1_id)
    expense_id = create_response.get_json()["id"]
    login_as(test_client, user1_id)

    response = test_client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 750}
    )

    assert response.status_code == 200
    assert response.get_json()["amount"] == "750.00"


def test_delete_expense(client):
    test_client, user1_id, user2_id = client
    create_response = create_test_expense(test_client, user1_id)
    expense_id = create_response.get_json()["id"]
    login_as(test_client, user1_id)

    response = test_client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200

    get_response = test_client.get(f"/expenses/{expense_id}")
    assert get_response.status_code == 404


def test_user_cannot_access_another_users_expense(client):
    test_client, user1_id, user2_id = client
    create_response = create_test_expense(test_client, user1_id)
    expense_id = create_response.get_json()["id"]
    login_as(test_client, user2_id)

    response = test_client.get(f"/expenses/{expense_id}")
    assert response.status_code == 404


def test_create_expense_with_invalid_amount(client):
    test_client, user1_id, user2_id = client
    login_as(test_client, user1_id)

    response = test_client.post(
        "/expenses",
        json={
            "title": "Lunch",
            "amount": -500,
            "category": "Food",
            "timestamp": "2026-11-01T12:00:00"
        }
    )

    assert response.status_code == 400


def test_create_expense_rejects_fractional_cents(client):
    test_client, user1_id, user2_id = client
    login_as(test_client, user1_id)

    response = test_client.post(
        "/expenses",
        json={
            "title": "Precise amount",
            "amount": "1.234",
            "category": "Other"
        }
    )

    assert response.status_code == 400
    assert "2 decimal places" in response.get_json()["error"]


def test_create_expense_preserves_timezone_in_utc(client):
    test_client, user1_id, user2_id = client
    login_as(test_client, user1_id)

    response = test_client.post(
        "/expenses",
        json={
            "title": "Offset time",
            "amount": "1.23",
            "category": "Other",
            "timestamp": "2026-01-01T12:00:00+05:00"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["timestamp"] == "2026-01-01T07:00:00+00:00"
    assert response.get_json()["amount"] == "1.23"


def test_create_expense_with_missing_fields(client):
    test_client, user1_id, user2_id = client
    login_as(test_client, user1_id)

    response = test_client.post(
        "/expenses",
        json={"title": "Lunch", "amount": 500}
    )

    assert response.status_code == 400


def test_user_cannot_delete_another_users_expense(client):
    test_client, user1_id, user2_id = client
    create_response = create_test_expense(test_client, user1_id)
    expense_id = create_response.get_json()["id"]
    login_as(test_client, user2_id)

    response = test_client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 404