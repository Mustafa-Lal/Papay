"""
Mechanic invoice service.

Creates a MechanicInvoice and adds it to the current
SQLAlchemy transaction.

This service does NOT commit.
The parent transaction controls commit/rollback.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_invoice import PaymentStatus
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice


def create_mechanic_invoice(
    db: Session,
    customer_id: int,
    plate_number: str,
    created_by: int,
    labor_charges: Decimal = Decimal("0.00"),
    payment_status: PaymentStatus = PaymentStatus.UNPAID,
) -> MechanicInvoice:

    # Verify that the mechanic customer exists.
    customer = db.scalar(
        select(MechanicCustomer).where(
            MechanicCustomer.id == customer_id
        )
    )

    if customer is None:
        raise ValueError(
            "Mechanic customer does not exist."
        )

    # Plate number is mandatory.
    if not plate_number or not plate_number.strip():
        raise ValueError(
            "Plate number is required."
        )

    # Labor charges cannot be negative.
    if labor_charges < Decimal("0.00"):
        raise ValueError(
            "Labor charges cannot be negative."
        )

    invoice = MechanicInvoice(
        customer_id=customer_id,
        plate_number=plate_number.strip(),
        labor_charges=labor_charges,
        payment_status=payment_status,
        created_by=created_by,
    )

    db.add(invoice)

    return invoice