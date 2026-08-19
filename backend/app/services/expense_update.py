from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def update_expense(
    db: Session,
    expense_id: int,
    description: str | None = None,
    amount: Decimal | None = None,
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
    # Update description
    # --------------------------------------------------

    if description is not None:

        description = description.strip()

        if not description:
            raise ValueError(
                "Expense description cannot be empty."
            )

        expense.description = description

    # --------------------------------------------------
    # Update amount
    # --------------------------------------------------

    if amount is not None:

        if amount < Decimal("0.00"):
            raise ValueError(
                "Expense amount cannot be negative."
            )

        expense.amount = amount

    return expense