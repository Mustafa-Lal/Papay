"""
Insurance invoice service.

Responsible for creating insurance invoice records.

This service does NOT commit the transaction.
The caller is responsible for commit/rollback.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import (
    InsuranceInvoice,
    PaymentStatus,
)


def create_insurance_invoice(
    db: Session,
    customer_id: int,
    plate_number: str,
    created_by: int,
    labor_charges: Decimal = Decimal("0.00"),
    payment_status: PaymentStatus = PaymentStatus.UNPAID,
) -> InsuranceInvoice:

    # Verify customer exists.
    customer = db.scalar(
        select(InsuranceCustomer).where(
            InsuranceCustomer.id == customer_id
        )
    )

    if customer is None:
        raise ValueError(
            "Insurance customer does not exist."
        )

    # Validate plate number.
    if not plate_number or not plate_number.strip():
        raise ValueError(
            "Plate number is required."
        )

    # Validate labor charges.
    if labor_charges < Decimal("0.00"):
        raise ValueError(
            "Labor charges cannot be negative."
        )

    invoice = InsuranceInvoice(
        customer_id=customer_id,
        plate_number=plate_number.strip(),
        labor_charges=labor_charges,
        payment_status=payment_status,
        created_by=created_by,
    )

    db.add(invoice)

    return invoice