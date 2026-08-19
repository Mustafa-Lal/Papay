from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.expense import Expense


def create_expense(
    db: Session,
    description: str,
    amount: Decimal,
    created_by: int,
) -> Expense:

    # --------------------------------------------------
    # Validate description
    # --------------------------------------------------

    if not description or not description.strip():
        raise ValueError(
            "Expense description is required."
        )

    description = description.strip()

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Expense amount cannot be negative."
        )

    # --------------------------------------------------
    # Create expense
    # --------------------------------------------------

    expense = Expense(
        description=description,
        amount=amount,
        created_by=created_by,
    )

    db.add(expense)

    return expense