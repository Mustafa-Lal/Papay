from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InsuranceCustomer(Base):
    __tablename__ = "insurance_customers"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    qid: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )