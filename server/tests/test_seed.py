import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


SERVER_DIR = Path(__file__).resolve().parents[1]


def run_python(source, environment):
    result = subprocess.run(
        [sys.executable, "-c", dedent(source)],
        cwd=SERVER_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_seeding_preserves_existing_data_and_is_repeatable(tmp_path):
    database_path = tmp_path / "existing.sqlite"
    environment = os.environ.copy()
    environment["SECRET_KEY"] = "test-secret-key"
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"
    environment["PYTHONPATH"] = str(SERVER_DIR)

    run_python(
        """
        from app import app
        from models import db, Expense, User

        with app.app_context():
            db.create_all()
            user = User(username="existing_user", email="existing@example.com")
            user.password_hash = "existing-password"
            db.session.add(user)
            db.session.flush()
            db.session.add(Expense(
                title="Keep this",
                amount=10,
                category="Other",
                user_id=user.id,
            ))
            db.session.commit()
        """,
        environment,
    )

    subprocess.run(
        [sys.executable, "seed.py"],
        cwd=SERVER_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        [sys.executable, "seed.py"],
        cwd=SERVER_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )

    run_python(
        """
        from app import app
        from models import db, Expense, User

        with app.app_context():
            assert User.query.count() == 3
            assert Expense.query.count() == 37
            assert Expense.query.filter_by(title="Keep this").count() == 1
        """,
        environment,
    )
