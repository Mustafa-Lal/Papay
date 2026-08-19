from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem


def delete_insurance_invoice(
    db: Session,
    invoice_id: int,
) -> None:

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
    # Delete all items belonging to invoice
    # --------------------------------------------------

    db.execute(
        delete(InsuranceItem).where(
            InsuranceItem.invoice_id == invoice_id
        )
    )

    # --------------------------------------------------
    # Delete invoice
    # --------------------------------------------------

    db.delete(invoice)