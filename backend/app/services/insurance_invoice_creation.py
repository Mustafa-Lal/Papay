"""
Insurance invoice creation orchestration service.

Creates an insurance customer, invoice, and all invoice
items inside one database transaction.

If any operation fails:
    - Customer is rolled back.
    - Invoice is rolled back.
    - All items are rolled back.

Images are intentionally NOT handled here.
Images are uploaded individually after the invoice exists.
"""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import (
    InsuranceInvoice,
    PaymentStatus,
)
from app.models.insurance_item import InsuranceItem

from app.services.insurance_customer import (
    create_insurance_customer,
)
from app.services.insurance_invoice import (
    create_insurance_invoice,
)
from app.services.insurance_item import (
    create_insurance_item,
)


@dataclass
class InsuranceItemData:
    description: str
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal = Decimal("0.00")


@dataclass
class InsuranceInvoiceCreationResult:
    customer: InsuranceCustomer
    invoice: InsuranceInvoice
    items: list[InsuranceItem]


def create_insurance_invoice_transaction(
    db: Session,
    *,
    customer_name: str | None = None,
    phone_number: str | None = None,
    qid: str | None = None,
    plate_number: str,
    labor_charges: Decimal = Decimal("0.00"),
    payment_status: PaymentStatus = PaymentStatus.UNPAID,
    created_by: int,
    items: list[InsuranceItemData],
) -> InsuranceInvoiceCreationResult:

    try:

        # --------------------------------------------------
        # 1. Create customer
        # --------------------------------------------------

        customer = create_insurance_customer(
            db=db,
            customer_name=customer_name,
            phone_number=phone_number,
            qid=qid,
        )

        # --------------------------------------------------
        # 2. Flush customer
        # --------------------------------------------------
        #
        # We need customer.id before creating the invoice.
        #
        # flush() sends the INSERT to the database but does
        # NOT commit the transaction.
        #
        # Therefore rollback is still possible.
        # --------------------------------------------------

        db.flush()

        # --------------------------------------------------
        # 3. Create invoice
        # --------------------------------------------------

        invoice = create_insurance_invoice(
            db=db,
            customer_id=customer.id,
            plate_number=plate_number,
            labor_charges=labor_charges,
            payment_status=payment_status,
            created_by=created_by,
        )

        db.flush()

        # --------------------------------------------------
        # 4. Create items
        # --------------------------------------------------

        created_items: list[InsuranceItem] = []

        for item_data in items:

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                commission=item_data.commission,
            )

            created_items.append(item)

        # --------------------------------------------------
        # 5. Everything succeeded
        # --------------------------------------------------

        db.commit()

        # Refresh objects so generated database values
        # such as IDs are available after commit.

        db.refresh(customer)
        db.refresh(invoice)

        for item in created_items:
            db.refresh(item)

        return InsuranceInvoiceCreationResult(
            customer=customer,
            invoice=invoice,
            items=created_items,
        )

    except Exception:

        # --------------------------------------------------
        # Something failed.
        #
        # Everything created above belongs to this same
        # transaction, so rollback removes all of it.
        # --------------------------------------------------

        db.rollback()

        raise