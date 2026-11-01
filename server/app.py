from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db
from resources.expense import expense_bp


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-this-to-a-secure-secret-key"

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(expense_bp)


@app.route("/")
def home():
    return jsonify({
        "message": "Personal Expense Tracker API is running."
    })


if __name__ == "__main__":
    app.run(port=5555, debug=True)