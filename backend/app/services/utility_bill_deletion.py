from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utility_bill import UtilityBill


def delete_utility_bill(
    db: Session,
    bill_id: int,
) -> None:

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
    # Delete bill
    # --------------------------------------------------

    db.delete(bill)