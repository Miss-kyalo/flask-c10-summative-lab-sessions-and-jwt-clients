from flask import request, session
from flask_restful import Resource

from models import Expense


class ExpenseList(Resource):
    def get(self):
        """Return the logged-in user's expenses, one page at a time."""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        # Read ?page= and ?per_page= from the URL
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            return {'error': 'page and per_page must be integers'}, 400
        if page < 1 or per_page < 1:
            return {'error': 'page and per_page must be at least 1'}, 400
        per_page = min(per_page, 100)

        pagination = (
            Expense.query.filter_by(user_id=user_id)
            .order_by(Expense.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            'items': [expense.to_dict() for expense in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }, 200