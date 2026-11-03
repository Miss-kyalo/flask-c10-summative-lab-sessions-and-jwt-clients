
from decimal import Decimal, InvalidOperation
from datetime import date

from flask import Blueprint, request, session

from models import db, Expense


expense_bp = Blueprint("expenses", __name__)


def expense_to_dict(expense):
    return {
        "id": expense.id,
        "description": expense.description,
        "amount": str(expense.amount),
        "category": expense.category,
        "date": expense.date.isoformat(),
        "user_id": expense.user_id
    }


def get_logged_in_user_id():
    return session.get("user_id")


def get_owned_expense(expense_id, user_id):
    return Expense.query.filter_by(
        id=expense_id,
        user_id=user_id
    ).first()


def validate_expense_data(data, partial=False):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    allowed_fields = {
        "description",
        "amount",
        "category",
        "date"
    }

    if set(data.keys()) - allowed_fields:
        return None, "Request contains unsupported fields."

    required_fields = {
        "description",
        "amount",
        "category",
        "date"
    }

    if not partial and not required_fields.issubset(data.keys()):
        return None, "All expense fields are required."

    cleaned_data = {}

    for field in ("description", "category"):
        if field in data:
            value = data[field]

            if not isinstance(value, str) or not value.strip():
                return None, f"{field} must be a non-empty string."

            cleaned_data[field] = value.strip()

    if "amount" in data:
        try:
            amount = Decimal(str(data["amount"]))

            if not amount.is_finite() or amount <= 0:
                return None, "Amount must be a positive number."

            if amount.as_tuple().exponent < -2:
                return None, "Amount cannot have more than two decimal places."

            if amount >= Decimal("100000000"):
                return None, "Amount is too large."

            cleaned_data["amount"] = amount

        except (InvalidOperation, ValueError, TypeError):
            return None, "Amount must be a valid number."

    if "date" in data:
        try:
            if not isinstance(data["date"], str):
                return None, "Date must use YYYY-MM-DD format."

            cleaned_data["date"] = date.fromisoformat(data["date"])

        except ValueError:
            return None, "Date must use YYYY-MM-DD format."

    return cleaned_data, None


@expense_bp.route("/expenses", methods=["GET"])
def get_expenses():
    user_id = get_logged_in_user_id()

    if not user_id:
        return {"error": "Unauthorized"}, 401

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

    except ValueError:
        return {
            "error": "page and per_page must be integers"
        }, 400

    if page < 1 or per_page < 1:
        return {
            "error": "page and per_page must be at least 1"
        }, 400

    per_page = min(per_page, 100)

    pagination = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return {
        "items": [
            expense_to_dict(expense)
            for expense in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }, 200


@expense_bp.route("/expenses", methods=["POST"])
def create_expense():
    user_id = get_logged_in_user_id()

    if not user_id:
        return {"error": "Unauthorized"}, 401

    data, error = validate_expense_data(
        request.get_json(silent=True),
        partial=False
    )

    if error:
        return {"error": error}, 400

    expense = Expense(
        description=data["description"],
        amount=data["amount"],
        category=data["category"],
        date=data["date"],
        user_id=user_id
    )

    try:
        db.session.add(expense)
        db.session.commit()

        return expense_to_dict(expense), 201

    except Exception:
        db.session.rollback()
        return {"error": "Unable to create expense."}, 500


@expense_bp.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    user_id = get_logged_in_user_id()

    if not user_id:
        return {"error": "Unauthorized"}, 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return {"error": "Expense not found."}, 404

    return expense_to_dict(expense), 200


@expense_bp.route("/expenses/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    user_id = get_logged_in_user_id()

    if not user_id:
        return {"error": "Unauthorized"}, 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return {"error": "Expense not found."}, 404

    data, error = validate_expense_data(
        request.get_json(silent=True),
        partial=True
    )

    if error:
        return {"error": error}, 400

    if not data:
        return {"error": "No valid fields provided."}, 400

    try:
        for field, value in data.items():
            setattr(expense, field, value)

        db.session.commit()

        return expense_to_dict(expense), 200

    except Exception:
        db.session.rollback()
        return {"error": "Unable to update expense."}, 500


@expense_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user_id = get_logged_in_user_id()

    if not user_id:
        return {"error": "Unauthorized"}, 401

    expense = get_owned_expense(expense_id, user_id)

    if not expense:
        return {"error": "Expense not found."}, 404

    try:
        db.session.delete(expense)
        db.session.commit()

        return {
            "message": "Expense deleted successfully."
        }, 200

    except Exception:
        db.session.rollback()
        return {"error": "Unable to delete expense."}, 500
