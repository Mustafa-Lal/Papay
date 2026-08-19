"""
Insurance customer service.

Responsible for creating insurance customer records.

This service does NOT commit the transaction.
The caller is responsible for commit/rollback.
"""

from sqlalchemy.orm import Session

from app.models.insurance_customer import InsuranceCustomer


def create_insurance_customer(
    db: Session,
    customer_name: str | None = None,
    phone_number: str | None = None,
    qid: str | None = None,
) -> InsuranceCustomer:

    customer = InsuranceCustomer(
        customer_name=customer_name,
        phone_number=phone_number,
        qid=qid,
    )

    db.add(customer)

    return customer