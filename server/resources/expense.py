
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request, session

from models import db, Expense


expense_bp = Blueprint("expenses", __name__)


def expense_to_dict(expense):
    """Convert an Expense object into JSON-friendly data."""
    return {
        "id": expense.id,
        "description": expense.description,
        "amount": str(expense.amount),
        "category": expense.category,
        "date": expense.date.isoformat(),
        "user_id": expense.user_id
    }


def get_logged_in_user_id():
    """Get the ID of the currently logged-in user."""
    return session.get("user_id")


def get_owned_expense(expense_id, user_id):
    """Find an expense only if it belongs to the logged-in user."""
    return Expense.query.filter_by(
        id=expense_id,
        user_id=user_id
    ).first()


def validate_expense_data(data, partial=False):
    """Validate expense fields before creating or updating an expense."""
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    allowed_fields = {"description", "amount", "category", "date"}

    if not data:
        return None, "Please provide expense details."

    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        return None, "Unknown fields: " + ", ".join(sorted(unknown_fields))

    required_fields = {"description", "amount", "category", "date"}

    if not partial:
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return None, "Missing fields: " + ", ".join(sorted(missing_fields))

    validated = {}

    if "description" in data:
        description = data["description"]
        if not isinstance(description, str) or not description.strip():
            return None, "Description must be a non-empty string."
        validated["description"] = description.strip()

    if "category" in data:
        category = data["category"]
        if not isinstance(category, str) or not category.strip():
            return None, "Category must be a non-empty string."
        validated["category"] = category.strip()

    if "amount" in data:
        try:
            amount = Decimal(str(data["amount"]))
            if not amount.is_finite() or amount <= 0:
                return None, "Amount must be a positive number."
            if amount.as_tuple().exponent < -2:
                return None, "Amount can have at most two decimal places."
            if amount >= Decimal("100000000"):
                return None, "Amount is too large."
        except (InvalidOperation, ValueError, TypeError):
            return None, "Amount must be a valid number."

        validated["amount"] = amount

    if "date" in data:
        try:
            validated["date"] = date.fromisoformat(data["date"])
        except (ValueError, TypeError):
            return None, "Date must use YYYY-MM-DD format."

    return validated, None


@expense_bp.route("/expenses", methods=["GET"])
def get_expenses():
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive."}), 400

        if per_page > 100:
            return jsonify({"error": "per_page cannot exceed 100."}), 400

        pagination = (
            Expense.query
            .filter_by(user_id=user_id)
            .order_by(Expense.date.desc(), Expense.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return jsonify({
            "expenses": [
                expense_to_dict(expense)
                for expense in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid pagination values."}), 400


@expense_bp.route("/expenses", methods=["POST"])
def create_expense():
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True)
    validated, error = validate_expense_data(data)

    if error:
        return jsonify({"error": error}), 400

    expense = Expense(
        description=validated["description"],
        amount=validated["amount"],
        category=validated["category"],
        date=validated["date"],
        user_id=user_id
    )

    try:
        db.session.add(expense)
        db.session.commit()

        return jsonify(expense_to_dict(expense)), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create the expense."}), 500


@expense_bp.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    expense = get_owned_expense(expense_id, user_id)

    if expense is None:
        return jsonify({"error": "Expense not found."}), 404

    return jsonify(expense_to_dict(expense)), 200


@expense_bp.route("/expenses/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    expense = get_owned_expense(expense_id, user_id)

    if expense is None:
        return jsonify({"error": "Expense not found."}), 404

    data = request.get_json(silent=True)
    validated, error = validate_expense_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    for field, value in validated.items():
        setattr(expense, field, value)

    try:
        db.session.commit()
        return jsonify(expense_to_dict(expense)), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not update the expense."}), 500


@expense_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user_id = get_logged_in_user_id()

    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    expense = get_owned_expense(expense_id, user_id)

    if expense is None:
        return jsonify({"error": "Expense not found."}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense deleted successfully."}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not delete the expense."}), 500
