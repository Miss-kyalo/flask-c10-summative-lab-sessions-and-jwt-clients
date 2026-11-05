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


def get_database_uri():
    db_url = os.environ.get("DATABASE_URL", "sqlite:///expense_tracker.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret-key")

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    is_debug = environment_flag("FLASK_DEBUG", False)
    SESSION_COOKIE_SECURE = environment_flag("SESSION_COOKIE_SECURE", not is_debug)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"