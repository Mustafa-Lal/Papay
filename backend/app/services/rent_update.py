from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rent import Rent


def update_rent(
    db: Session,
    rent_id: int,
    amount: Decimal,
) -> Rent:

    # --------------------------------------------------
    # Find rent
    # --------------------------------------------------

    rent = db.scalar(
        select(Rent).where(
            Rent.id == rent_id
        )
    )

    if rent is None:
        raise ValueError(
            "Rent not found."
        )

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Rent amount cannot be negative."
        )

    # --------------------------------------------------
    # Update amount
    # --------------------------------------------------

    rent.amount = amount

    return rent