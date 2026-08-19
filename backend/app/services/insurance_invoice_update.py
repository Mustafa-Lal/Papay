from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_invoice import (
    InsuranceInvoice,
    PaymentStatus,
)


def update_insurance_invoice(
    db: Session,
    invoice_id: int,
    plate_number: str | None = None,
    labor_charges: Decimal | None = None,
    payment_status: PaymentStatus | None = None,
) -> InsuranceInvoice:

    # --------------------------------------------------
    # Find invoice
    # --------------------------------------------------

    invoice = db.scalar(
        select(InsuranceInvoice).where(
            InsuranceInvoice.id == invoice_id
        )
    )

    if invoice is None:
        raise ValueError(
            "Insurance invoice not found."
        )

    # --------------------------------------------------
    # Update plate number
    # --------------------------------------------------

    if plate_number is not None:

        plate_number = plate_number.strip()

        if not plate_number:
            raise ValueError(
                "Plate number cannot be empty."
            )

        invoice.plate_number = plate_number

    # --------------------------------------------------
    # Update labor charges
    # --------------------------------------------------

    if labor_charges is not None:

        if labor_charges < Decimal("0.00"):
            raise ValueError(
                "Labor charges cannot be negative."
            )

        invoice.labor_charges = labor_charges

    # --------------------------------------------------
    # Update payment status
    # --------------------------------------------------

    if payment_status is not None:

        if not isinstance(
            payment_status,
            PaymentStatus,
        ):
            raise ValueError(
                "Invalid payment status."
            )

        invoice.payment_status = payment_status

    return invoice