from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rent import Rent


def get_rent(
    db: Session,
    year: int,
    month: int,
) -> Rent:

    # --------------------------------------------------
    # Validate month
    # --------------------------------------------------

    if month < 1 or month > 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

    # --------------------------------------------------
    # Fetch rent for the requested period
    # --------------------------------------------------

    rent = db.scalar(
        select(Rent).where(
            Rent.year == year,
            Rent.month == month,
        )
    )

    if rent is None:
        raise ValueError(
            "Rent not found for the requested month."
        )

    return rent