from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.profit import Profit


def get_profits(
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
        Profit.is_active.is_(True),
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
            Profit.created_at >= start_datetime
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
            Profit.created_at < end_datetime
        )

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    total = db.scalar(
        select(func.count())
        .select_from(Profit)
        .where(*filters)
    )

    # --------------------------------------------------
    # Fetch profits
    # --------------------------------------------------

    profits = db.scalars(
        select(Profit)
        .where(*filters)
        .order_by(
            Profit.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {
        "profits": [
            {
                "id": profit.id,
                "name": profit.name,
                "amount": profit.amount,
                "created_at": profit.created_at,
            }
            for profit in profits
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (
                offset + len(profits)
            ) < total,
        },
    }


def get_profits_this_month(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    today = date.today()

    start_date = today.replace(
        day=1
    )

    return get_profits(
        db=db,
        start_date=start_date,
        end_date=today,
        limit=limit,
        offset=offset,
    )