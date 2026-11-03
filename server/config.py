import os


def environment_flag(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


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
    SESSION_COOKIE_SECURE = environment_flag("SESSION_COOKIE_SECURE", True)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"