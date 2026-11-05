import argparse
from datetime import timezone
from decimal import Decimal
import random

from faker import Faker
from app import app
from models import db, Expense, User

fake = Faker()

CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
]


def seed_database(reset=False):
    with app.app_context():
        if reset:
            print("Resetting database tables...")
            db.drop_all()
            db.create_all()
        else:
            db.create_all()

        print("Seeding demo users...")
        user_details = [
            ("demo_user", "demo@example.com"),
            ("other_user", "other@example.com"),
        ]
        users = []

        for username, email in user_details:
            user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if user and (user.username != username or user.email != email):
                raise ValueError(
                    f"Cannot seed {email}: the username or email is already in use."
                )

            if user is None:
                user = User(username=username, email=email)
                user.password_hash = "Password123!"
                db.session.add(user)
                db.session.flush()

            users.append(user)

        expenses_to_add = []
        for user in users:
            existing_count = Expense.query.filter_by(user_id=user.id).count()
            if existing_count == 0:
                for _ in range(18):
                    raw_amount = round(random.uniform(5.00, 350.00), 2)
                    amount = Decimal(str(raw_amount))

                    naive_dt = fake.date_time_between(start_date="-6M", end_date="now")
                    aware_dt = naive_dt.replace(tzinfo=timezone.utc)

                    expenses_to_add.append(
                        Expense(
                            title=fake.sentence(nb_words=3).rstrip("."),
                            amount=amount,
                            category=random.choice(CATEGORIES),
                            timestamp=aware_dt,
                            user_id=user.id,
                        )
                    )

        if expenses_to_add:
            db.session.add_all(expenses_to_add)
            db.session.commit()

        print(
            f"Database seeded successfully with {len(users)} users and "
            f"{len(expenses_to_add)} new expenses."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with demo data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate database tables before seeding.",
    )
    args = parser.parse_args()

    seed_database(reset=args.reset)