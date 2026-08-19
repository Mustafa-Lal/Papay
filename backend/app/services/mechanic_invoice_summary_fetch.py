from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice


def get_mechanic_customers(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
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
    # Validate date range
    # --------------------------------------------------

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise ValueError(
            "Start date cannot be after end date."
        )

    # --------------------------------------------------
    # Build filters
    # --------------------------------------------------

    filters = [
        MechanicCustomer.is_active.is_(True),
    ]

    # --------------------------------------------------
    # Start date
    # --------------------------------------------------

    if start_date is not None:

        start_datetime = datetime.combine(
            start_date,
            time.min,
        ).replace(
            tzinfo=timezone.utc
        )

        filters.append(
            MechanicInvoice.created_at
            >= start_datetime
        )

    # --------------------------------------------------
    # End date
    # --------------------------------------------------

    if end_date is not None:

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        ).replace(
            tzinfo=timezone.utc
        )

        filters.append(
            MechanicInvoice.created_at
            < end_datetime
        )

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
        .where(*filters)
    )

    # --------------------------------------------------
    # Fetch customer + invoice summaries
    #
    # One row = one invoice.
    # --------------------------------------------------

    rows = db.execute(
        select(
            MechanicCustomer,
            MechanicInvoice,
        )
        .join(
            MechanicInvoice,
            MechanicInvoice.customer_id
            == MechanicCustomer.id,
        )
        .where(*filters)
        .order_by(
            MechanicInvoice.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Build response
    # --------------------------------------------------

    return {
        "customers": [
            {
                "customer_id": customer.id,
                "name": customer.customer_name,
                "phone_number": customer.phone_number,
                "invoice_id": invoice.id,
                "plate_number": invoice.plate_number,
                "payment_status": (
                    invoice.payment_status.value
                ),
                "invoice_date": invoice.created_at,
            }
            for customer, invoice in rows
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


def get_mechanic_customers_this_month(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    today = date.today()

    start_date = today.replace(
        day=1
    )

    return get_mechanic_customers(
        db=db,
        start_date=start_date,
        end_date=today,
        limit=limit,
        offset=offset,
    )