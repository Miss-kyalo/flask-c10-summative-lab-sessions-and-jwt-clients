from flask import request, session
from flask_restful import Resource

from models import db, User


MAX_BCRYPT_PASSWORD_BYTES = 72


def password_is_supported(password):
    try:
        return len(password.encode("utf-8")) <= MAX_BCRYPT_PASSWORD_BYTES
    except UnicodeEncodeError:
        return False


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not isinstance(username, str) or not isinstance(email, str) or not isinstance(password, str):
            return {"error": "Username, email and password are required"}, 422

        username = username.strip()
        email = email.strip().lower()

        if not username or not email:
            return {"error": "Username and email cannot be empty"}, 422

        if len(password) < 8:
            return {"error": "Password must be at least 8 characters"}, 422

        if not password_is_supported(password):
            return {"error": "Password must be at most 72 UTF-8 bytes"}, 422

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return {"error": "Username or email already exists"}, 422

        new_user = User(
            username=username,
            email=email
        )

        # The model hashes the password through this setter.
        new_user.password_hash = password

        try:
            db.session.add(new_user)
            db.session.commit()
            session.clear()
            session["user_id"] = new_user.id
        except Exception:
            db.session.rollback()
            return {"error": "Could not create account"}, 500

        return {
            "message": "Account created successfully",
            "user": new_user.to_dict()
        }, 201


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        email = data.get("email")
        password = data.get("password")

        if not isinstance(email, str) or not isinstance(password, str):
            return {"error": "Email and password are required"}, 422

        email = email.strip().lower()

        if not email or not password:
            return {"error": "Email and password are required"}, 422

        if not password_is_supported(password):
            return {"error": "Invalid email or password"}, 401

        user = User.query.filter_by(email=email).first()

        if not user or not user.authenticate(password):
            return {"error": "Invalid email or password"}, 401

        session.clear()
        session["user_id"] = user.id

        return {
            "message": "Login successful",
            "user": user.to_dict()
        }, 200


class Logout(Resource):
    def delete(self):
        session.clear()

        return {
            "message": "Logout successful"
        }, 200


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)

        if not user:
            session.clear()
            return {"error": "Unauthorized"}, 401

        return user.to_dict(), 200