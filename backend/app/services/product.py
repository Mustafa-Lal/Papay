from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(
    db: Session,
    description: str,
    quantity: Decimal,
    unit_price: Decimal,
    created_by: int,
) -> Product:

    # --------------------------------------------------
    # Validate description
    # --------------------------------------------------

    if not description or not description.strip():
        raise ValueError(
            "Product description is required."
        )

    description = description.strip()

    # --------------------------------------------------
    # Validate quantity
    # --------------------------------------------------

    if quantity <= Decimal("0.00"):
        raise ValueError(
            "Product quantity must be greater than zero."
        )

    # --------------------------------------------------
    # Validate unit price
    # --------------------------------------------------

    if unit_price < Decimal("0.00"):
        raise ValueError(
            "Product unit price cannot be negative."
        )

    # --------------------------------------------------
    # Create product
    # --------------------------------------------------

    product = Product(
        description=description,
        quantity=quantity,
        unit_price=unit_price,
        created_by=created_by,
    )

    db.add(product)

    return product