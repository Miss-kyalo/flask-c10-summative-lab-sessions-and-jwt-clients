import os
import subprocess
import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]


def test_missing_secret_key_fails_fast():
    environment = os.environ.copy()
    environment.pop("SECRET_KEY", None)
    environment["PYTHONPATH"] = str(SERVER_DIR)

    result = subprocess.run(
        [sys.executable, "-c", "from config import Config"],
        cwd=SERVER_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Set the SECRET_KEY environment variable" in result.stderr
