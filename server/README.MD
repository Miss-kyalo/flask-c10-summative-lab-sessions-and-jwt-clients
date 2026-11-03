Personal Expense Tracker API
A robust, secure, and production-ready RESTful API built with Flask, Flask-RESTful, and Flask-SQLAlchemy. It features user authentication with session management, comprehensive validation, pagination, and a complete CRUD interface for tracking personal expenses.

**Features**
User Authentication: Secure signup, login, logout, and session verification using flask-bcrypt for password hashing and Flask sessions.

Expense Management: Full CRUD operations (Create, Read, Update, Delete) restricted to the authenticated user.

Robust Validation: Strict input checking (sanitizing strings, validating decimal precision for currency amounts, checking unknown fields, and ISO datetime validation).

Pagination & Sorting: Automatically paginates and sorts expense lists by timestamp (newest first).

Database Seeding: Built-in Faker-powered script to quickly populate demo users and realistic mock expenses.

**Tech Stack**
Backend: Python, Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt

Database: SQLite (default) / SQLAlchemy ORM

Utilities: Faker (for seeding).

