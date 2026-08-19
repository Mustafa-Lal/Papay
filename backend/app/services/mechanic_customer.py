"""
Mechanic customer service.

This service creates a MechanicCustomer and adds it to the
current SQLAlchemy transaction.

It does NOT commit.

The caller controls:
    - flush()
    - commit()
    - rollback()
"""


from sqlalchemy.orm import Session

from app.models.mechanic_customer import MechanicCustomer


def create_mechanic_customer(
    db: Session,
    customer_name: str | None = None,
    phone_number: str | None = None,
    qid: str | None = None,
) -> MechanicCustomer:

    customer = MechanicCustomer(
        customer_name=customer_name,
        phone_number=phone_number,
        qid=qid,
    )

    db.add(customer)

    return customer