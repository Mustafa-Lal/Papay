from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def update_product(
    db: Session,
    product_id: int,
    description: str | None = None,
    quantity: Decimal | None = None,
    unit_price: Decimal | None = None,
) -> Product:

    # --------------------------------------------------
    # Find product
    # --------------------------------------------------

    product = db.scalar(
        select(Product).where(
            Product.id == product_id
        )
    )

    if product is None:
        raise ValueError(
            "Product not found."
        )

    # --------------------------------------------------
    # Update description
    # --------------------------------------------------

    if description is not None:

        description = description.strip()

        if not description:
            raise ValueError(
                "Product description cannot be empty."
            )

        product.description = description

    # --------------------------------------------------
    # Update quantity
    # --------------------------------------------------

    if quantity is not None:

        if quantity <= Decimal("0.00"):
            raise ValueError(
                "Product quantity must be greater than zero."
            )

        product.quantity = quantity

    # --------------------------------------------------
    # Update unit price
    # --------------------------------------------------

    if unit_price is not None:

        if unit_price < Decimal("0.00"):
            raise ValueError(
                "Product unit price cannot be negative."
            )

        product.unit_price = unit_price

    return product