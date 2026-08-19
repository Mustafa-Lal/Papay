from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.salary import Salary


def create_salary(
    db: Session,
    name: str,
    amount: Decimal,
    created_by: int,
) -> Salary:

    # --------------------------------------------------
    # Validate name
    # --------------------------------------------------

    if not name or not name.strip():
        raise ValueError(
            "Salary recipient name is required."
        )

    name = name.strip()

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Salary amount cannot be negative."
        )

    # --------------------------------------------------
    # Create salary
    # --------------------------------------------------

    salary = Salary(
        name=name,
        amount=amount,
        created_by=created_by,
    )

    db.add(salary)

    return salary