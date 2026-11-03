
from flask import request, session
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User


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
            return {"error": "Invalid registration information"}, 422

        if len(password) < 8:
            return {"error": "Password must be at least 8 characters"}, 422

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return {"error": "Username or email already exists"}, 422

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"error": "Could not create account"}, 500

        return {
            "message": "Account created successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
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

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid email or password"}, 401

        session.clear()
        session["user_id"] = user.id

        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, 200


class Logout(Resource):
    def delete(self):
        session.clear()
        return {"message": "Logout successful"}, 200


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)

        if not user:
            session.clear()
            return {"error": "Unauthorized"}, 401

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200


