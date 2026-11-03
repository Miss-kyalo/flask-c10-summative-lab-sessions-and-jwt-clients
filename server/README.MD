Personal Expense Tracker API
A robust, secure, and production-ready RESTful API built with Flask, Flask-RESTful, and Flask-SQLAlchemy. It features user authentication with session management, comprehensive validation, pagination, and a complete CRUD interface for tracking personal expenses.

**Features**
User Authentication: Secure signup, login, logout, and session verification using flask-bcrypt for password hashing and Flask sessions.

Expense Management: Full CRUD operations (Create, Read, Update, Delete) restricted to the authenticated user. Currency amounts are limited to two decimal places, and timestamps are stored/returned in UTC.

Robust Validation: Strict input checking (sanitizing strings, validating decimal precision for currency amounts, checking unknown fields, and ISO datetime validation).

Pagination & Sorting: Automatically paginates and sorts expense lists by timestamp (newest first).

Database Seeding: Built-in Faker-powered script to quickly populate demo users and realistic mock expenses.

**Tech Stack**
Backend: Python, Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt

Database: SQLite (default) / SQLAlchemy ORM

Utilities: Faker (for seeding).

**Configuration**
Set `SECRET_KEY` before starting the API. `SESSION_COOKIE_SECURE` defaults to `true`; set it to `false` only for local development over plain HTTP. Secure cookies should remain enabled when deployed behind HTTPS.

Existing databases must be migrated when changing the expense amount column from floating point to fixed precision. `db.create_all()` does not alter existing tables.
