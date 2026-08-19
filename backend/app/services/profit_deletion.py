from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profit import Profit


def deactivate_profit(
    db: Session,
    profit_id: int,
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
    # Deactivate profit
    # --------------------------------------------------

    profit.is_active = False

    return profit