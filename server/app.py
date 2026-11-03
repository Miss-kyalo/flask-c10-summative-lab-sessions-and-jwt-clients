
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from models import db
from resources.auth import Signup, Login, Logout, CheckSession
from resources.expense import expense_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

app.register_blueprint(expense_bp)


@app.route("/")
def home():
    return jsonify({
        "message": "Personal Expense Tracker API is running."
    }), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)
