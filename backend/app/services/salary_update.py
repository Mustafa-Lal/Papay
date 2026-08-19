from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.salary import Salary


def update_salary(
    db: Session,
    salary_id: int,
    name: str | None = None,
    amount: Decimal | None = None,
) -> Salary:

    # --------------------------------------------------
    # Find salary
    # --------------------------------------------------

    salary = db.scalar(
        select(Salary).where(
            Salary.id == salary_id
        )
    )

    if salary is None:
        raise ValueError(
            "Salary not found."
        )

    # --------------------------------------------------
    # Update name
    # --------------------------------------------------

    if name is not None:

        name = name.strip()

        if not name:
            raise ValueError(
                "Salary name cannot be empty."
            )

        salary.name = name

    # --------------------------------------------------
    # Update amount
    # --------------------------------------------------

    if amount is not None:

        if amount < Decimal("0.00"):
            raise ValueError(
                "Salary amount cannot be negative."
            )

        salary.amount = amount

    return salary