import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key-change-later"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///expense_tracker.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False