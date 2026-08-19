from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mechanic_customer import MechanicCustomer


def update_mechanic_customer(
    db: Session,
    customer_id: int,
    customer_name: str | None = None,
    phone_number: str | None = None,
    qid: str | None = None,
) -> MechanicCustomer:

    # --------------------------------------------------
    # Find customer
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
    # Update customer name
    # --------------------------------------------------

    if customer_name is not None:

        customer_name = customer_name.strip()

        if not customer_name:
            raise ValueError(
                "Customer name cannot be empty."
            )

        customer.customer_name = customer_name

    # --------------------------------------------------
    # Update phone number
    # --------------------------------------------------

    if phone_number is not None:
        customer.phone_number = phone_number.strip()

    # --------------------------------------------------
    # Update QID
    # --------------------------------------------------

    if qid is not None:
        customer.qid = qid.strip()

    return customer