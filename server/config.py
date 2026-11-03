import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY or not SECRET_KEY.strip():
        raise ValueError(
            "No SECRET_KEY set for the application. "
            "Set the SECRET_KEY environment variable."
        )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///expense_tracker.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False