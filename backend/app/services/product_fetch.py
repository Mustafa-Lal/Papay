from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_products(
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
    # Build base query
    # --------------------------------------------------

    filters = [
        Product.is_active.is_(True),
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
            Product.created_at >= start_datetime
        )

    # --------------------------------------------------
    # End date
    #
    # Use the next day at midnight so the entire
    # end_date is included.
    # --------------------------------------------------

    if end_date is not None:

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        ).replace(
            tzinfo=timezone.utc
        )

        filters.append(
            Product.created_at < end_datetime
        )

    # --------------------------------------------------
    # Count total matching products
    # --------------------------------------------------

    total = db.scalar(
        select(func.count())
        .select_from(Product)
        .where(*filters)
    )

    # --------------------------------------------------
    # Fetch products
    # --------------------------------------------------

    products = db.scalars(
        select(Product)
        .where(*filters)
        .order_by(
            Product.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {
        "products": [
            {
                "id": product.id,
                "description": product.description,
                "quantity": product.quantity,
                "unit_price": product.unit_price,
                "created_at": product.created_at,
            }
            for product in products
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (
                offset + len(products)
            ) < total,
        },
    }

def get_products_this_month(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    today = date.today()

    start_date = today.replace(
        day=1
    )

    return get_products(
        db=db,
        start_date=start_date,
        end_date=today,
        limit=limit,
        offset=offset,
    )