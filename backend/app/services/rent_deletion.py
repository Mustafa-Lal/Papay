from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rent import Rent


def delete_rent(
    db: Session,
    rent_id: int,
) -> None:

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
    # Delete rent
    # --------------------------------------------------

    db.delete(rent)