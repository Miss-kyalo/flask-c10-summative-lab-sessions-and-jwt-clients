from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request, session

from models import db, Expense


expense_bp = Blueprint("expenses", __name__)


def get_logged_in_user_id():
    user_id = session.get("user_id")

    try:
        return int(user_id)
    except (TypeError, ValueError):
        return None


def expense_to_dict(expense):
    return {
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "timestamp": (
            expense.timestamp.isoformat()
            if expense.timestamp else None
        ),
        "user_id": expense.user_id
    }


def get_owned_expense(expense_id, user_id):
    return Expense.query.filter_by(
        id=expense_id,
        user_id=user_id
    ).first()


def validate_expense_data(data, partial=False):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    allowed_fields = {"title", "amount", "category", "timestamp"}

    if not data:
        return None, "Please provide expense details."

    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        return None, "Unknown fields: " + ", ".join(sorted(unknown_fields))

    required_fields = {"title", "amount", "category"}

    if not partial:
        missing_fields = required_fields - set(data.keys())

        if missing_fields:
            return None, "Missing fields: " + ", ".join(sorted(missing_fields))

    validated = {}

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return None, "Title must be a non-empty string."

        validated["title"] = data["title"].strip()

    if "category" in data:
        if not isinstance(data["category"], str) or not data["category"].strip():
            return None, "Category must be a non-empty string."

        validated["category"] = data["category"].strip()

    if "amount" in data:
        try:
            amount = Decimal(str(data["amount"]))

            if not amount.is_finite() or amount <= 0:
                return None, "Amount must be greater than zero."

            if amount >= 100000000:
                return None, "Amount is too large."

            validated["amount"] = float(amount)

        except (InvalidOperation, ValueError, TypeError):
            return None, "Amount must be a valid number."

    if "timestamp" in data:
        if not isinstance(data["timestamp"], str):
            return None, "Timestamp must be a valid date and time."

        try:
            validated["timestamp"] = datetime.fromisoformat(
                data["timestamp"]
            )
        except ValueError:
            return None, "Invalid timestamp format."

    return validated, None


@expense_bp.route("/expenses", methods=["GET"])
def get_expenses():
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({
            "error": "Page and per_page must be integers."
        }), 400

    if page < 1 or per_page < 1:
        return jsonify({
            "error": "Page and per_page must be at least 1."
        }), 400

    per_page = min(per_page, 100)

    pagination = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.timestamp.desc(), Expense.id.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "items": [
            expense_to_dict(expense)
            for expense in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }), 200


@expense_bp.route("/expenses", methods=["POST"])
def create_expense():
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    validated, error = validate_expense_data(data)

    if error:
        return jsonify({"error": error}), 400

    expense = Expense(
        title=validated["title"],
        amount=validated["amount"],
        category=validated["category"],
        user_id=user_id,
        timestamp=validated.get("timestamp", datetime.utcnow())
    )

    try:
        db.session.add(expense)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create expense."}), 500

    return jsonify(expense_to_dict(expense)), 201


@expense_bp.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return jsonify({"error": "Expense not found."}), 404

    return jsonify(expense_to_dict(expense)), 200


@expense_bp.route("/expenses/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return jsonify({"error": "Expense not found."}), 404

    data = request.get_json(silent=True)
    validated, error = validate_expense_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    for field, value in validated.items():
        setattr(expense, field, value)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not update expense."}), 500

    return jsonify(expense_to_dict(expense)), 200


@expense_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return jsonify({"error": "Expense not found."}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not delete expense."}), 500

    return jsonify({
        "message": "Expense deleted successfully."
    }), 200