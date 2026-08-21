from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice


def get_insurance_invoices_by_plate(
    db: Session,
    plate_number: str,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    # --------------------------------------------------
    # Validate pagination
    # --------------------------------------------------

    if limit <= 0:
        raise ValueError(
            "Limit must be greater than zero."
        )

    if offset < 0:
        raise ValueError(
            "Offset cannot be negative."
        )

    # --------------------------------------------------
    # Validate plate number
    # --------------------------------------------------

    if not plate_number or not plate_number.strip():
        raise ValueError(
            "Plate number is required."
        )

    plate_number = plate_number.strip()

    # --------------------------------------------------
    # Count matching invoices
    # --------------------------------------------------

    total = db.scalar(
        select(func.count(InsuranceInvoice.id))
        .join(
            InsuranceCustomer,
            InsuranceInvoice.customer_id
            == InsuranceCustomer.id,
        )
        .where(
            InsuranceInvoice.plate_number
            == plate_number,
            InsuranceInvoice.is_active.is_(True),
        )
    )

    # --------------------------------------------------
    # Fetch invoice summaries
    # --------------------------------------------------

    rows = db.execute(
        select(
            InsuranceInvoice,
            InsuranceCustomer,
        )
        .join(
            InsuranceCustomer,
            InsuranceInvoice.customer_id
            == InsuranceCustomer.id,
        )
        .where(
            InsuranceInvoice.plate_number
            == plate_number,
            InsuranceInvoice.is_active.is_(True),
        )
        .order_by(
            InsuranceInvoice.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {
        "invoices": [
            {
                "invoice_id": invoice.id,
                "customer_id": customer.id,
                "customer_name": customer.customer_name,
                "phone_number": customer.phone_number,
                "plate_number": invoice.plate_number,
                "payment_status": (
                    invoice.payment_status.value
                ),
                "invoice_date": invoice.created_at,
            }
            for invoice, customer in rows
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (
                offset + len(rows)
            ) < total,
        },
    }