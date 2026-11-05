import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from models import db, bcrypt
from resources.auth import Signup, Login, Logout, CheckSession
from resources.expense import expense_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, supports_credentials=True)

    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    api = Api(app)
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session")

    app.register_blueprint(expense_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred"}), 500

    @app.route("/")
    def home():
        return jsonify({
            "message": "Personal Expense Tracker API is running."
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "").strip().lower() in {
        "true",
        "1",
    }
    app.run(port=5555, debug=debug_mode)