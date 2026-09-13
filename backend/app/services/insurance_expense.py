from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.insurance_expense import InsuranceExpense


def create_insurance_expense(
    db: Session,
    description: str,
    price: Decimal,
    created_by: int,
) -> InsuranceExpense:

    # --------------------------------------------------
    # Validate description
    # --------------------------------------------------

    if not description or not description.strip():
        raise ValueError(
            "Insurance expense description is required."
        )

    description = description.strip()

    # --------------------------------------------------
    # Validate price
    # --------------------------------------------------

    if price < Decimal("0.00"):
        raise ValueError(
            "Insurance expense price cannot be negative."
        )

    # --------------------------------------------------
    # Create insurance expense
    # --------------------------------------------------

    expense = InsuranceExpense(
        description=description,
        price=price,
        created_by=created_by,
    )

    db.add(expense)

    return expense


def get_insurance_expenses(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    if offset < 0:
        raise ValueError("Offset cannot be negative.")

    filters = [
        InsuranceExpense.is_active.is_(True),
    ]

    total = db.scalar(
        select(func.count()).select_from(InsuranceExpense).where(*filters)
    ) or 0

    stmt = (
        select(InsuranceExpense)
        .where(*filters)
        .order_by(InsuranceExpense.created_at.desc(), InsuranceExpense.id.desc())
        .limit(limit)
        .offset(offset)
    )

    expenses = list(db.scalars(stmt).all())

    return {
        "expenses": expenses,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + len(expenses)) < total,
        },
    }


def update_insurance_expense(
    db: Session,
    expense_id: int,
    description: str | None = None,
    price: Decimal | None = None,
) -> InsuranceExpense:

    expense = db.scalar(
        select(InsuranceExpense).where(
            InsuranceExpense.id == expense_id,
            InsuranceExpense.is_active.is_(True),
        )
    )

    if expense is None:
        raise ValueError("Insurance expense not found.")

    if description is not None:
        description = description.strip()
        if not description:
            raise ValueError("Insurance expense description cannot be empty.")
        expense.description = description

    if price is not None:
        if price < Decimal("0.00"):
            raise ValueError("Insurance expense price cannot be negative.")
        expense.price = price

    return expense


def deactivate_insurance_expense(
    db: Session,
    expense_id: int,
) -> InsuranceExpense:

    expense = db.scalar(
        select(InsuranceExpense).where(
            InsuranceExpense.id == expense_id,
            InsuranceExpense.is_active.is_(True),
        )
    )

    if expense is None:
        raise ValueError("Insurance expense not found.")

    expense.is_active = False

    return expense
