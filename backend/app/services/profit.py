from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.profit import Profit


def create_profit(
    db: Session,
    name: str,
    amount: Decimal,
    created_by: int,
) -> Profit:

    # --------------------------------------------------
    # Validate name
    # --------------------------------------------------

    if not name or not name.strip():
        raise ValueError(
            "Profit name is required."
        )

    name = name.strip()

    # --------------------------------------------------
    # Validate amount
    # --------------------------------------------------

    if amount < Decimal("0.00"):
        raise ValueError(
            "Profit amount cannot be negative."
        )

    # --------------------------------------------------
    # Create profit
    # --------------------------------------------------

    profit = Profit(
        name=name,
        amount=amount,
        created_by=created_by,
    )

    db.add(profit)

    return profit