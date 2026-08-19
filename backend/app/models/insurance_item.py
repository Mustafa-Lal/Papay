"""
Insurance invoice item model.

Stores individual items belonging to an insurance invoice.

The item total is not stored because it is derived from
quantity, unit price, and the applicable commission logic.
"""

from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InsuranceItem(Base):
    __tablename__ = "insurance_items"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey(
            "insurance_invoices.id"
        ),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    commission: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )