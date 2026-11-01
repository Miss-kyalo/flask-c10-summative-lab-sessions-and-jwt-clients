from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from resources.expense import expense_bp


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

jwt = JWTManager(app)
migrate = Migrate(app, db)

app.register_blueprint(expense_bp)


@app.route("/")
def home():
    return jsonify({
        "message": "Personal Expense Tracker API is running."
    }), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)