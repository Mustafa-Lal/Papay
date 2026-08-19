"""
Mechanic item service.

Creates a MechanicItem and adds it to the current
SQLAlchemy transaction.

This service does NOT commit.
The parent transaction controls commit/rollback.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem


def create_mechanic_item(
    db: Session,
    invoice_id: int,
    description: str,
    quantity: Decimal,
    unit_price: Decimal,
    commission: Decimal = Decimal("0.00"),
) -> MechanicItem:

    # --------------------------------------------------
    # Verify invoice exists
    # --------------------------------------------------

    invoice = db.scalar(
        select(MechanicInvoice).where(
            MechanicInvoice.id == invoice_id
        )
    )

    if invoice is None:
        raise ValueError(
            "Mechanic invoice does not exist."
        )

    # --------------------------------------------------
    # Validate description
    # --------------------------------------------------

    if not description or not description.strip():
        raise ValueError(
            "Item description is required."
        )

    # --------------------------------------------------
    # Validate quantity
    # --------------------------------------------------

    if quantity <= Decimal("0.00"):
        raise ValueError(
            "Quantity must be greater than zero."
        )

    # --------------------------------------------------
    # Validate unit price
    # --------------------------------------------------

    if unit_price < Decimal("0.00"):
        raise ValueError(
            "Unit price cannot be negative."
        )

    # --------------------------------------------------
    # Validate commission
    # --------------------------------------------------

    if commission < Decimal("0.00"):
        raise ValueError(
            "Commission cannot be negative."
        )

    # --------------------------------------------------
    # Create item
    # --------------------------------------------------

    item = MechanicItem(
        invoice_id=invoice_id,
        description=description.strip(),
        quantity=quantity,
        unit_price=unit_price,
        commission=commission,
    )

    db.add(item)

    return item