
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

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_signup(client):
    response = client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert "Secure" in response.headers["Set-Cookie"]
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Lax" in response.headers["Set-Cookie"]
    assert response.get_json()["user"]["username"] == "siraj"


def test_signup_duplicate_email(client):
    client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/signup",
        json={
            "username": "another",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_signup_short_password(client):
    response = client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422


def test_signup_rejects_password_over_bcrypt_byte_limit(client):
    response = client.post(
        "/signup",
        json={
            "username": "long_password",
            "email": "long-password@example.com",
            "password": "p" * 73
        }
    )

    assert response.status_code == 422
    assert "72 UTF-8 bytes" in response.get_json()["error"]


def test_signup_accepts_password_within_bcrypt_byte_limit(client):
    response = client.post(
        "/signup",
        json={
            "username": "max_password",
            "email": "max-password@example.com",
            "password": "p" * 72
        }
    )

    assert response.status_code == 201


def test_login_rejects_password_over_bcrypt_byte_limit(client):
    response = client.post(
        "/login",
        json={
            "email": "nobody@example.com",
            "password": "p" * 73
        }
    )

    assert response.status_code == 401


def test_login(client):
    client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Login successful"


def test_login_wrong_password(client):
    client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "siraj@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_check_session(client):
    client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    client.post(
        "/login",
        json={
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    response = client.get("/check_session")

    assert response.status_code == 200
    assert response.get_json()["username"] == "siraj"


def test_check_session_without_login(client):
    response = client.get("/check_session")

    assert response.status_code == 401


def test_logout(client):
    client.post(
        "/signup",
        json={
            "username": "siraj",
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    client.post(
        "/login",
        json={
            "email": "siraj@example.com",
            "password": "password123"
        }
    )

    response = client.delete("/logout")

    assert response.status_code == 200

    check_response = client.get("/check_session")
    assert check_response.status_code == 401
