from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def deactivate_product(
    db: Session,
    product_id: int,
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
    # Deactivate product
    # --------------------------------------------------

    product.is_active = False

    return product