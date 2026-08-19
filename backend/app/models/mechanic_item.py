from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MechanicItem(Base):
    __tablename__ = "mechanic_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("mechanic_invoices.id"),
        nullable=False,
        index=True,
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