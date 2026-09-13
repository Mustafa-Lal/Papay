from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.insurance_income import InsuranceIncome


def create_insurance_income(
    db: Session,
    description: str,
    price: Decimal,
    created_by: int,
) -> InsuranceIncome:

    # --------------------------------------------------
    # Validate description
    # --------------------------------------------------

    if not description or not description.strip():
        raise ValueError(
            "Insurance income description is required."
        )

    description = description.strip()

    # --------------------------------------------------
    # Validate price
    # --------------------------------------------------

    if price < Decimal("0.00"):
        raise ValueError(
            "Insurance income price cannot be negative."
        )

    # --------------------------------------------------
    # Create insurance income
    # --------------------------------------------------

    income = InsuranceIncome(
        description=description,
        price=price,
        created_by=created_by,
    )

    db.add(income)

    return income


def get_insurance_incomes(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    if offset < 0:
        raise ValueError("Offset cannot be negative.")

    filters = [
        InsuranceIncome.is_active.is_(True),
    ]

    total = db.scalar(
        select(func.count()).select_from(InsuranceIncome).where(*filters)
    ) or 0

    stmt = (
        select(InsuranceIncome)
        .where(*filters)
        .order_by(InsuranceIncome.created_at.desc(), InsuranceIncome.id.desc())
        .limit(limit)
        .offset(offset)
    )

    incomes = list(db.scalars(stmt).all())

    return {
        "incomes": incomes,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + len(incomes)) < total,
        },
    }


def update_insurance_income(
    db: Session,
    income_id: int,
    description: str | None = None,
    price: Decimal | None = None,
) -> InsuranceIncome:

    income = db.scalar(
        select(InsuranceIncome).where(
            InsuranceIncome.id == income_id,
            InsuranceIncome.is_active.is_(True),
        )
    )

    if income is None:
        raise ValueError("Insurance income not found.")

    if description is not None:
        description = description.strip()
        if not description:
            raise ValueError("Insurance income description cannot be empty.")
        income.description = description

    if price is not None:
        if price < Decimal("0.00"):
            raise ValueError("Insurance income price cannot be negative.")
        income.price = price

    return income


def deactivate_insurance_income(
    db: Session,
    income_id: int,
) -> InsuranceIncome:

    income = db.scalar(
        select(InsuranceIncome).where(
            InsuranceIncome.id == income_id,
            InsuranceIncome.is_active.is_(True),
        )
    )

    if income is None:
        raise ValueError("Insurance income not found.")

    income.is_active = False

    return income
