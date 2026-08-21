from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.models.insurance_image import InsuranceImage


def get_insurance_customer_details(
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
        select(InsuranceCustomer).where(
            InsuranceCustomer.id == customer_id
        )
    )

    if customer is None:
        raise ValueError(
            "Insurance customer not found."
        )

    # --------------------------------------------------
    # Fetch customer's invoices
    # --------------------------------------------------

    invoices = db.scalars(
        select(InsuranceInvoice)
        .where(
            InsuranceInvoice.customer_id == customer_id,
            InsuranceInvoice.is_active.is_(True)
        )
        .order_by(
            InsuranceInvoice.created_at.desc()
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
            select(InsuranceItem)
            .where(
                InsuranceItem.invoice_id == invoice.id,
                InsuranceItem.is_active.is_(True)
            )
            .order_by(
                InsuranceItem.id.asc()
            )
        ).all()

        # --------------------------------------------------
        # Fetch invoice images
        # --------------------------------------------------

        images = db.scalars(
            select(InsuranceImage)
            .where(
                InsuranceImage.invoice_id == invoice.id
            )
            .order_by(
                InsuranceImage.id.asc()
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

                # ------------------------------------------
                # Items
                # ------------------------------------------

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

                # ------------------------------------------
                # Images
                # ------------------------------------------

                "images": [
                    {
                        "id": image.id,
                        "type": image.image_type.value,
                        "file_path": image.file_path,
                    }
                    for image in images
                ],
            }
        )

    # --------------------------------------------------
    # Return customer + invoices
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


def get_insurance_invoice_full_details(db: Session, invoice_id: int) -> dict | None:
    # Fetch invoice
    invoice = db.scalar(
        select(InsuranceInvoice).where(
            InsuranceInvoice.id == invoice_id,
            InsuranceInvoice.is_active.is_(True)
        )
    )
    if invoice is None:
        return None

    # Fetch customer
    customer = db.scalar(
        select(InsuranceCustomer).where(InsuranceCustomer.id == invoice.customer_id)
    )

    # Fetch items
    items = db.scalars(
        select(InsuranceItem)
        .where(
            InsuranceItem.invoice_id == invoice.id,
            InsuranceItem.is_active.is_(True)
        )
        .order_by(InsuranceItem.id.asc())
    ).all()

    # Fetch images
    images = db.scalars(
        select(InsuranceImage)
        .where(InsuranceImage.invoice_id == invoice.id)
        .order_by(InsuranceImage.id.asc())
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
        ],
        "images": [
            {
                "id": image.id,
                "invoice_id": image.invoice_id,
                "image_type": image.image_type.value,
                "file_path": image.file_path,
            }
            for image in images
        ]
    }