from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utility_bill import (
    UtilityBill,
    UtilityBillType,
)


def create_utility_bill(
    db: Session,
    bill_type: UtilityBillType,
    amount: Decimal,
    year: int,
    month: int,
    created_by: int,
) -> UtilityBill:

    # --------------------------------------------------
    # Validate bill type
    # --------------------------------------------------

    if not isinstance(bill_type, UtilityBillType):
        raise ValueError(
            "Invalid utility bill type."
        )

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
            "Bill amount cannot be negative."
        )

    # --------------------------------------------------
    # Reject future months
    # --------------------------------------------------

    current_date = date.today()

    requested_period = (year, month)
    current_period = (
        current_date.year,
        current_date.month,
    )

    if requested_period > current_period:
        raise ValueError(
            "Cannot add a bill for a future month."
        )

    # --------------------------------------------------
    # Check duplicate bill
    # --------------------------------------------------

    existing_bill = db.scalar(
        select(UtilityBill).where(
            UtilityBill.bill_type == bill_type,
            UtilityBill.year == year,
            UtilityBill.month == month,
        )
    )

    if existing_bill is not None:
        raise ValueError(
            "This utility bill has already been added for this month."
        )

    # --------------------------------------------------
    # Create bill
    # --------------------------------------------------

    bill = UtilityBill(
        bill_type=bill_type,
        amount=amount,
        year=year,
        month=month,
        created_by=created_by,
    )

    db.add(bill)

    return bill