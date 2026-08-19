from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utility_bill import UtilityBill


def update_utility_bill(
    db: Session,
    bill_id: int,
    amount: Decimal,
) -> UtilityBill:

    # --------------------------------------------------
    # Find bill
    # --------------------------------------------------

    bill = db.scalar(
        select(UtilityBill).where(
            UtilityBill.id == bill_id
        )
    )

    if bill is None:
        raise ValueError(
            "Utility bill not found."
        )

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Utility bill amount cannot be negative."
        )

    # --------------------------------------------------
    # Update amount
    # --------------------------------------------------

    bill.amount = amount

    return bill