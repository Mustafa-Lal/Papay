from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rent import Rent


def create_rent(
    db: Session,
    amount: Decimal,
    year: int,
    month: int,
    created_by: int,
) -> Rent:

    # --------------------------------------------------
    # Validate month
    # --------------------------------------------------

    if month < 1 or month > 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Rent amount cannot be negative."
        )

    # --------------------------------------------------
    # Validate requested month is not in the future
    # --------------------------------------------------

    current_date = date.today()

    requested_period = (year, month)
    current_period = (
        current_date.year,
        current_date.month,
    )

    if requested_period > current_period:
        raise ValueError(
            "Cannot add rent for a future month."
        )

    # --------------------------------------------------
    # Check whether rent already exists
    # --------------------------------------------------

    existing_rent = db.scalar(
        select(Rent).where(
            Rent.year == year,
            Rent.month == month,
        )
    )

    if existing_rent is not None:
        raise ValueError(
            "Rent already added for this month."
        )

    # --------------------------------------------------
    # Create rent
    # --------------------------------------------------

    rent = Rent(
        amount=amount,
        year=year,
        month=month,
        created_by=created_by,
    )

    db.add(rent)

    return rent