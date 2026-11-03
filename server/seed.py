import random
from faker import Faker
from app import app
from models import db, User, Expense

fake = Faker()

CATEGORIES = ['Food & Dining', 'Transportation', 'Utilities', 'Entertainment', 'Healthcare', 'Shopping']

def seed_database():
    with app.app_context():
        db.create_all()

        print("Seeding demo users without deleting existing data...")
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
            if not user.expenses:
                for _ in range(18):
                    expenses_to_add.append(
                        Expense(
                            title=fake.sentence(nb_words=3).rstrip("."),
                            amount=round(random.uniform(5.00, 350.00), 2),
                            category=random.choice(CATEGORIES),
                            timestamp=fake.date_time_between(
                                start_date="-6M",
                                end_date="now"
                            ),
                            user_id=user.id
                        )
                    )

        db.session.add_all(expenses_to_add)
        db.session.commit()

        print(
            f"Database seeded with {len(users)} demo users and "
            f"{len(expenses_to_add)} expenses."
        )

if __name__ == '__main__':
    seed_database()
    