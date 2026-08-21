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

    from sqlalchemy import update
    # --------------------------------------------------
    # Soft-delete all items belonging to invoice
    # --------------------------------------------------

    db.execute(
        update(InsuranceItem)
        .where(InsuranceItem.invoice_id == invoice_id)
        .values(is_active=False)
    )

    # --------------------------------------------------
    # Soft-delete invoice
    # --------------------------------------------------

    invoice.is_active = False