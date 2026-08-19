from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.insurance_invoice import PaymentStatus


class MechanicInvoice(Base):
    __tablename__ = "mechanic_invoices"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("mechanic_customers.id"),
        nullable=False,
        index=True,
    )

    plate_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    labor_charges: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        nullable=False,
        default=PaymentStatus.UNPAID,
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("access_keys.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )