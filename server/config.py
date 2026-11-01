import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key-change-later"
    )

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "development-jwt-secret-change-later"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///expense_tracker.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)