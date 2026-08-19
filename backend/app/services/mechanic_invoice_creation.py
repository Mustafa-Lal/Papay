"""
Atomic mechanic invoice creation.

Creates:

    MechanicCustomer
        ↓
    MechanicInvoice
        ↓
    MechanicItem(s)

Everything is committed together.

If anything fails, the entire transaction is rolled back.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.insurance_invoice import PaymentStatus
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice

from app.services.mechanic_customer import (
    create_mechanic_customer,
)

from app.services.mechanic_invoice import (
    create_mechanic_invoice,
)

from app.services.mechanic_item import (
    create_mechanic_item,
)


def create_mechanic_invoice_transaction(
    db: Session,
    customer_name: str | None,
    phone_number: str | None,
    qid: str | None,
    plate_number: str,
    created_by: int,
    labor_charges: Decimal = Decimal("0.00"),
    payment_status: PaymentStatus = PaymentStatus.UNPAID,
    items: list[dict] | None = None,
) -> MechanicInvoice:

    if items is None:
        items = []

    try:
        # --------------------------------------------------
        # 1. Create customer
        # --------------------------------------------------

        customer = create_mechanic_customer(
            db=db,
            customer_name=customer_name,
            phone_number=phone_number,
            qid=qid,
        )

        db.flush()

        # --------------------------------------------------
        # 2. Create invoice
        # --------------------------------------------------

        invoice = create_mechanic_invoice(
            db=db,
            customer_id=customer.id,
            plate_number=plate_number,
            created_by=created_by,
            labor_charges=labor_charges,
            payment_status=payment_status,
        )

        db.flush()

        # --------------------------------------------------
        # 3. Create items
        # --------------------------------------------------

        for item_data in items:

            create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description=item_data["description"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                commission=item_data.get(
                    "commission",
                    Decimal("0.00"),
                ),
            )

        # --------------------------------------------------
        # 4. Flush everything
        # --------------------------------------------------

        db.flush()

        # --------------------------------------------------
        # 5. Commit entire transaction
        # --------------------------------------------------

        db.commit()

        return invoice

    except Exception:
        # --------------------------------------------------
        # Any failure → rollback EVERYTHING
        # --------------------------------------------------

        db.rollback()

        raise