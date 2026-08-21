from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice


def get_mechanic_invoices_by_plate(
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
        select(func.count(MechanicInvoice.id))
        .join(
            MechanicCustomer,
            MechanicInvoice.customer_id
            == MechanicCustomer.id,
        )
        .where(
            MechanicInvoice.plate_number
            == plate_number,
            MechanicInvoice.is_active.is_(True),
        )
    )

    # --------------------------------------------------
    # Fetch invoice summaries
    # --------------------------------------------------

    rows = db.execute(
        select(
            MechanicInvoice,
            MechanicCustomer,
        )
        .join(
            MechanicCustomer,
            MechanicInvoice.customer_id
            == MechanicCustomer.id,
        )
        .where(
            MechanicInvoice.plate_number
            == plate_number,
            MechanicInvoice.is_active.is_(True),
        )
        .order_by(
            MechanicInvoice.created_at.desc()
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