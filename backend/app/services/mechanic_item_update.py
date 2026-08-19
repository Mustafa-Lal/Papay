from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mechanic_item import MechanicItem


def update_mechanic_item(
    db: Session,
    item_id: int,
    description: str | None = None,
    quantity: Decimal | None = None,
    unit_price: Decimal | None = None,
    commission: Decimal | None = None,
) -> MechanicItem:

    # --------------------------------------------------
    # Find item
    # --------------------------------------------------

    item = db.scalar(
        select(MechanicItem).where(
            MechanicItem.id == item_id
        )
    )

    if item is None:
        raise ValueError(
            "Mechanic item not found."
        )

    # --------------------------------------------------
    # Update description
    # --------------------------------------------------

    if description is not None:

        description = description.strip()

        if not description:
            raise ValueError(
                "Item description cannot be empty."
            )

        item.description = description

    # --------------------------------------------------
    # Update quantity
    # --------------------------------------------------

    if quantity is not None:

        if quantity <= Decimal("0.00"):
            raise ValueError(
                "Item quantity must be greater than zero."
            )

        item.quantity = quantity

    # --------------------------------------------------
    # Update unit price
    # --------------------------------------------------

    if unit_price is not None:

        if unit_price < Decimal("0.00"):
            raise ValueError(
                "Item unit price cannot be negative."
            )

        item.unit_price = unit_price

    # --------------------------------------------------
    # Update commission
    # --------------------------------------------------

    if commission is not None:

        if commission < Decimal("0.00"):
            raise ValueError(
                "Item commission cannot be negative."
            )

        item.commission = commission

    return item