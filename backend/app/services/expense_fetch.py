from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def get_expenses(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    # --------------------------------------------------
    # Validate pagination
    # --------------------------------------------------

    if limit <= 0:
        raise ValueError(
            "Limit must be greater than zero."
        )

    if offset < 0:
        raise ValueError(
            "Offset cannot be negative."
        )

    # --------------------------------------------------
    # Validate date range
    # --------------------------------------------------

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise ValueError(
            "Start date cannot be after end date."
        )

    # --------------------------------------------------
    # Build filters
    # --------------------------------------------------

    filters = [
        Expense.is_active.is_(True),
    ]

    # --------------------------------------------------
    # Start date
    # --------------------------------------------------

    if start_date is not None:

        start_datetime = datetime.combine(
            start_date,
            time.min,
        ).replace(
            tzinfo=timezone.utc
        )

        filters.append(
            Expense.created_at >= start_datetime
        )

    # --------------------------------------------------
    # End date
    # --------------------------------------------------

    if end_date is not None:

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        ).replace(
            tzinfo=timezone.utc
        )

        filters.append(
            Expense.created_at < end_datetime
        )

    # --------------------------------------------------
    # Count matching expenses
    # --------------------------------------------------

    total = db.scalar(
        select(func.count())
        .select_from(Expense)
        .where(*filters)
    )

    # --------------------------------------------------
    # Fetch expenses
    # --------------------------------------------------

    expenses = db.scalars(
        select(Expense)
        .where(*filters)
        .order_by(
            Expense.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {
        "expenses": [
            {
                "id": expense.id,
                "description": expense.description,
                "amount": expense.amount,
                "created_at": expense.created_at,
            }
            for expense in expenses
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (
                offset + len(expenses)
            ) < total,
        },
    }


def get_expenses_this_month(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    today = date.today()

    start_date = today.replace(
        day=1
    )

    return get_expenses(
        db=db,
        start_date=start_date,
        end_date=today,
        limit=limit,
        offset=offset,
    )