import os
import subprocess
import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]


def test_session_cookie_security_defaults():
    from config import Config

    assert Config.SESSION_COOKIE_SECURE is True
    assert Config.SESSION_COOKIE_HTTPONLY is True
    assert Config.SESSION_COOKIE_SAMESITE == "Lax"


def test_session_cookie_security_flag_parses_explicit_values(monkeypatch):
    from config import environment_flag

    monkeypatch.setenv("TEST_COOKIE_FLAG", "false")
    assert environment_flag("TEST_COOKIE_FLAG", True) is False

    monkeypatch.setenv("TEST_COOKIE_FLAG", "yes")
    assert environment_flag("TEST_COOKIE_FLAG", False) is True


def test_missing_secret_key_uses_development_fallback():
    environment = os.environ.copy()
    environment.pop("SECRET_KEY", None)
    environment["PYTHONPATH"] = str(SERVER_DIR)

    result = subprocess.run(
        [sys.executable, "-c", "from config import Config; print(Config.SECRET_KEY)"],
        cwd=SERVER_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "dev-fallback-secret-key"
