from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer

def update_customer(
    db: Session,
    customer_id: int,
    customer_name: str | None = None,
    phone_number: str | None = None,
    qid: str | None = None,
) -> InsuranceCustomer:

    # Find the customer
    customer = db.scalar(
        select(InsuranceCustomer).where(
            InsuranceCustomer.id == customer_id
        )
    )

    if customer is None:
        raise ValueError(
            "Insurance customer not found."
        )

    # Update name if provided
    if customer_name is not None:
        customer_name = customer_name.strip()

        if not customer_name:
            raise ValueError(
                "Customer name cannot be empty."
            )

        customer.customer_name = customer_name

    # Update phone number if provided
    if phone_number is not None:
        customer.phone_number = phone_number.strip()

    # Update QID if provided
    if qid is not None:
        customer.qid = qid.strip()

    return customer