from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.salary import Salary


def get_salaries(
    db: Session,
    year: int,
    month: int,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    # --------------------------------------------------
    # Validate month
    # --------------------------------------------------

    if month < 1 or month > 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

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
    # Build monthly date range
    # --------------------------------------------------

    start_date = date(
        year,
        month,
        1,
    )

    if month == 12:
        next_month = date(
            year + 1,
            1,
            1,
        )
    else:
        next_month = date(
            year,
            month + 1,
            1,
        )

    start_datetime = datetime.combine(
        start_date,
        time.min,
    ).replace(
        tzinfo=timezone.utc
    )

    end_datetime = datetime.combine(
        next_month,
        time.min,
    ).replace(
        tzinfo=timezone.utc
    )

    # --------------------------------------------------
    # Filters
    # --------------------------------------------------

    filters = [
        Salary.created_at >= start_datetime,
        Salary.created_at < end_datetime,
        Salary.is_active.is_(True),
    ]

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    total = db.scalar(
        select(func.count())
        .select_from(Salary)
        .where(*filters)
    )

    # --------------------------------------------------
    # Fetch salaries
    # --------------------------------------------------

    salaries = db.scalars(
        select(Salary)
        .where(*filters)
        .order_by(
            Salary.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "salaries": [
            {
                "id": salary.id,
                "name": salary.name,
                "amount": salary.amount,
                "created_at": salary.created_at,
            }
            for salary in salaries
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (
                offset + len(salaries)
            ) < total,
        },
    }