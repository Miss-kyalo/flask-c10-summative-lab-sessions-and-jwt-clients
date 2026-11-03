# seed.py
import random
from faker import Faker
from app import app  # Import your Flask application instance
from models import db, User, Expense

fake = Faker()

CATEGORIES = ['Food & Dining', 'Transportation', 'Utilities', 'Entertainment', 'Healthcare', 'Shopping']

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding test users...")
        # 1. Primary demo user
        demo_user = User(
            username="demo_user",
            email="demo@example.com"
        )
        demo_user.password_hash = "Password123!"

        # 2. Secondary user to test data isolation
        other_user = User(
            username="other_user",
            email="other@example.com"
        )
        other_user.password_hash = "Password123!"

        db.session.add_all([demo_user, other_user])
        db.session.commit()

        users = [demo_user, other_user]
        expenses_to_add = []

        print("Generating mock expenses...")
        for user in users:
            # Generate 18 mock expenses per user
            for _ in range(18):
                expense = Expense(
                    title=fake.sentence(nb_words=3).rstrip('.'),
                    amount=round(random.uniform(5.00, 350.00), 2),
                    category=random.choice(CATEGORIES),
                    timestamp=fake.date_time_between(start_date='-6M', end_date='now'),
                    user_id=user.id
                )
                expenses_to_add.append(expense)

        db.session.add_all(expenses_to_add)
        db.session.commit()

        print(f"Database successfully seeded with {len(users)} users and {len(expenses_to_add)} expenses!")

if __name__ == '__main__':
    seed_database()