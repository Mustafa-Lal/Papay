from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem


def get_mechanic_customer_details(
    db: Session,
    customer_id: int,
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
    # Fetch active customer
    # --------------------------------------------------

    customer = db.scalar(
        select(MechanicCustomer).where(
            MechanicCustomer.id == customer_id
        )
    )

    if customer is None:
        raise ValueError(
            "Mechanic customer not found."
        )

    # --------------------------------------------------
    # Fetch customer's invoices
    # --------------------------------------------------

    invoices = db.scalars(
        select(MechanicInvoice)
        .where(
            MechanicInvoice.customer_id == customer_id,
            MechanicInvoice.is_active.is_(True)
        )
        .order_by(
            MechanicInvoice.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Build invoice details
    # --------------------------------------------------

    invoice_details = []

    for invoice in invoices:

        # --------------------------------------------------
        # Fetch invoice items
        # --------------------------------------------------

        items = db.scalars(
            select(MechanicItem)
            .where(
                MechanicItem.invoice_id == invoice.id,
                MechanicItem.is_active.is_(True)
            )
            .order_by(
                MechanicItem.id.asc()
            )
        ).all()

        invoice_details.append(
            {
                "id": invoice.id,
                "plate_number": invoice.plate_number,
                "invoice_date": invoice.created_at,
                "labor_charges": invoice.labor_charges,
                "payment_status": (
                    invoice.payment_status.value
                ),
                "items": [
                    {
                        "id": item.id,
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "commission": item.commission,
                    }
                    for item in items
                ],
            }
        )

    # --------------------------------------------------
    # Return customer + invoices + items
    # --------------------------------------------------

    return {
        "customer": {
            "id": customer.id,
            "name": customer.customer_name,
            "phone_number": customer.phone_number,
            "qid": customer.qid,
        },
        "invoices": invoice_details,
    }


def get_mechanic_invoice_full_details(db: Session, invoice_id: int) -> dict | None:
    # Fetch invoice
    invoice = db.scalar(
        select(MechanicInvoice).where(
            MechanicInvoice.id == invoice_id,
            MechanicInvoice.is_active.is_(True)
        )
    )
    if invoice is None:
        return None

    # Fetch customer
    customer = db.scalar(
        select(MechanicCustomer).where(MechanicCustomer.id == invoice.customer_id)
    )

    # Fetch items
    items = db.scalars(
        select(MechanicItem)
        .where(
            MechanicItem.invoice_id == invoice.id,
            MechanicItem.is_active.is_(True)
        )
        .order_by(MechanicItem.id.asc())
    ).all()

    return {
        "id": invoice.id,
        "customer_id": invoice.customer_id,
        "plate_number": invoice.plate_number,
        "labor_charges": invoice.labor_charges,
        "payment_status": invoice.payment_status.value,
        "created_by": invoice.created_by,
        "created_at": invoice.created_at,
        "customer": {
            "id": customer.id,
            "customer_name": customer.customer_name,
            "phone_number": customer.phone_number,
            "qid": customer.qid,
        },
        "items": [
            {
                "id": item.id,
                "invoice_id": item.invoice_id,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "commission": item.commission,
            }
            for item in items
        ]
    }