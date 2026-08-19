from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def deactivate_expense(
    db: Session,
    expense_id: int,
) -> Expense:

    # --------------------------------------------------
    # Find expense
    # --------------------------------------------------

    expense = db.scalar(
        select(Expense).where(
            Expense.id == expense_id
        )
    )

    if expense is None:
        raise ValueError(
            "Expense not found."
        )

    # --------------------------------------------------
    # Deactivate expense
    # --------------------------------------------------

    expense.is_active = False

    return expense