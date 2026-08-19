from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profit import Profit


def update_profit(
    db: Session,
    profit_id: int,
    name: str | None = None,
    amount: Decimal | None = None,
) -> Profit:

    # --------------------------------------------------
    # Find profit
    # --------------------------------------------------

    profit = db.scalar(
        select(Profit).where(
            Profit.id == profit_id
        )
    )

    if profit is None:
        raise ValueError(
            "Profit not found."
        )

    # --------------------------------------------------
    # Update name
    # --------------------------------------------------

    if name is not None:

        name = name.strip()

        if not name:
            raise ValueError(
                "Profit name cannot be empty."
            )

        profit.name = name

    # --------------------------------------------------
    # Update amount
    # --------------------------------------------------

    if amount is not None:

        if amount < Decimal("0.00"):
            raise ValueError(
                "Profit amount cannot be negative."
            )

        profit.amount = amount

    return profit