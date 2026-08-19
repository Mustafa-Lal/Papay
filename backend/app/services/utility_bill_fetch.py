from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utility_bill import (
    UtilityBill,
    UtilityBillType,
)


def get_utility_bills(
    db: Session,
    year: int,
    month: int,
) -> list[UtilityBill]:

    # --------------------------------------------------
    # Validate month
    # --------------------------------------------------

    if month < 1 or month > 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

    # --------------------------------------------------
    # Fetch all utility bills for the period
    # --------------------------------------------------

    bills = db.scalars(
        select(UtilityBill)
        .where(
            UtilityBill.year == year,
            UtilityBill.month == month,
        )
        .order_by(
            UtilityBill.bill_type.asc()
        )
    ).all()

    return bills