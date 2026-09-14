"""
Insurance finance report service.

Fetches all active expenses and incomes for a given date range and
returns a single combined payload suitable for generating a printed report.

Unlike the paginated list endpoints, this service returns every matching
record (no limit/offset) ordered chronologically so the report reads
top-to-bottom by date.

Aggregate totals are computed via SQL SUM to avoid loading large amounts
of data into Python memory.
"""

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.insurance_expense import InsuranceExpense
from app.models.insurance_income import InsuranceIncome

_ZERO = Decimal("0.00")


def get_insurance_finance_report(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """
    Return a combined expense + income report for the given date range.

    Parameters
    ----------
    db         : Active database session.
    start_date : Inclusive start date (UTC midnight). None means no lower bound.
    end_date   : Inclusive end date (records up to end-of-day). None means no upper bound.

    Returns
    -------
    dict with keys:
        start_date     -- echoed back for the report header
        end_date       -- echoed back for the report header
        expenses       -- list of {id, description, price, created_at}
        incomes        -- list of {id, description, price, created_at}
        total_expense  -- Decimal sum of all expense prices
        total_income   -- Decimal sum of all income prices
        net            -- total_income minus total_expense (can be negative)
        expense_count  -- number of expense records
        income_count   -- number of income records

    Raises
    ------
    ValueError
        If start_date is later than end_date.
    """

    # --------------------------------------------------
    # Validate date range
    # --------------------------------------------------

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise ValueError("Start date cannot be after end date.")

    # --------------------------------------------------
    # Build UTC-aware datetime bounds
    # (same technique used across all fetch services)
    # --------------------------------------------------

    start_datetime: datetime | None = None
    end_datetime: datetime | None = None

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min,
        ).replace(tzinfo=timezone.utc)

    if end_date is not None:
        # Use start of next day as an exclusive upper bound so that
        # records created at any time on end_date are included.
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        ).replace(tzinfo=timezone.utc)

    # --------------------------------------------------
    # Build shared filters for expenses
    # --------------------------------------------------

    expense_filters = [InsuranceExpense.is_active.is_(True)]

    if start_datetime is not None:
        expense_filters.append(InsuranceExpense.created_at >= start_datetime)

    if end_datetime is not None:
        expense_filters.append(InsuranceExpense.created_at < end_datetime)

    # --------------------------------------------------
    # Build shared filters for incomes
    # --------------------------------------------------

    income_filters = [InsuranceIncome.is_active.is_(True)]

    if start_datetime is not None:
        income_filters.append(InsuranceIncome.created_at >= start_datetime)

    if end_datetime is not None:
        income_filters.append(InsuranceIncome.created_at < end_datetime)

    # --------------------------------------------------
    # Fetch all matching expenses -- ordered ASC for printing
    # --------------------------------------------------

    expense_rows = db.scalars(
        select(InsuranceExpense)
        .where(*expense_filters)
        .order_by(
            InsuranceExpense.created_at.asc(),
            InsuranceExpense.id.asc(),
        )
    ).all()

    # --------------------------------------------------
    # Fetch all matching incomes -- ordered ASC for printing
    # --------------------------------------------------

    income_rows = db.scalars(
        select(InsuranceIncome)
        .where(*income_filters)
        .order_by(
            InsuranceIncome.created_at.asc(),
            InsuranceIncome.id.asc(),
        )
    ).all()

    # --------------------------------------------------
    # Aggregate totals via SQL SUM (avoids summing in Python)
    # --------------------------------------------------

    total_expense = Decimal(
        str(
            db.scalar(
                select(
                    func.coalesce(func.sum(InsuranceExpense.price), _ZERO)
                ).where(*expense_filters)
            )
            or _ZERO
        )
    )

    total_income = Decimal(
        str(
            db.scalar(
                select(
                    func.coalesce(func.sum(InsuranceIncome.price), _ZERO)
                ).where(*income_filters)
            )
            or _ZERO
        )
    )

    # --------------------------------------------------
    # Build and return response dict
    # --------------------------------------------------

    return {
        "start_date": start_date,
        "end_date": end_date,
        "expenses": [
            {
                "id": e.id,
                "description": e.description,
                "price": e.price,
                "created_at": e.created_at,
            }
            for e in expense_rows
        ],
        "incomes": [
            {
                "id": i.id,
                "description": i.description,
                "price": i.price,
                "created_at": i.created_at,
            }
            for i in income_rows
        ],
        "total_expense": total_expense,
        "total_income": total_income,
        "net": total_income - total_expense,
        "expense_count": len(expense_rows),
        "income_count": len(income_rows),
    }
