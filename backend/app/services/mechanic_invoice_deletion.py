from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem


def delete_mechanic_invoice(
    db: Session,
    invoice_id: int,
) -> None:

    # --------------------------------------------------
    # Find invoice
    # --------------------------------------------------

    invoice = db.scalar(
        select(MechanicInvoice).where(
            MechanicInvoice.id == invoice_id
        )
    )

    if invoice is None:
        raise ValueError(
            "Mechanic invoice not found."
        )

    from sqlalchemy import update
    # --------------------------------------------------
    # Soft-delete all items belonging to invoice
    # --------------------------------------------------

    db.execute(
        update(MechanicItem)
        .where(MechanicItem.invoice_id == invoice_id)
        .values(is_active=False)
    )

    # --------------------------------------------------
    # Soft-delete invoice
    # --------------------------------------------------

    invoice.is_active = False