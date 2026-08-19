"""
Insurance invoice item service.

Responsible for creating individual items belonging
to an insurance invoice.

This service does NOT commit the transaction.
The caller is responsible for commit/rollback.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem


def create_insurance_item(
    db: Session,
    invoice_id: int,
    description: str,
    quantity: Decimal,
    unit_price: Decimal,
    commission: Decimal = Decimal("0.00"),
) -> InsuranceItem:

    # Verify invoice exists.
    invoice = db.scalar(
        select(InsuranceInvoice).where(
            InsuranceInvoice.id == invoice_id
        )
    )

    if invoice is None:
        raise ValueError(
            "Insurance invoice does not exist."
        )

    # Validate description.
    if not description or not description.strip():
        raise ValueError(
            "Item description is required."
        )

    # Validate quantity.
    if quantity <= Decimal("0.00"):
        raise ValueError(
            "Quantity must be greater than zero."
        )

    # Validate unit price.
    if unit_price < Decimal("0.00"):
        raise ValueError(
            "Unit price cannot be negative."
        )

    # Validate commission.
    if commission < Decimal("0.00"):
        raise ValueError(
            "Commission cannot be negative."
        )

    item = InsuranceItem(
        invoice_id=invoice_id,
        description=description.strip(),
        quantity=quantity,
        unit_price=unit_price,
        commission=commission,
    )

    db.add(item)

    return item