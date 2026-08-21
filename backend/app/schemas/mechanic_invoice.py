"""
Pydantic schemas for mechanic invoice API requests and responses.

Creation follows the mechanic invoice hierarchy:

    Customer
        ↓
    Invoice
        ↓
    Items

Mechanic invoices do not have an image entity.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.insurance_invoice import PaymentStatus
from app.schemas.product import PaginationResponse


# ==========================================================
# CUSTOMER
# ==========================================================

class MechanicCustomerCreate(BaseModel):
    """
    Customer information submitted when creating an invoice.

    Customers are created as part of the invoice creation
    workflow and are not created independently.
    """

    customer_name: str | None = None
    phone_number: str | None = None
    qid: str | None = None

    @field_validator(
        "customer_name",
        "phone_number",
        "qid",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

        return value


class MechanicCustomerUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing mechanic customer.
    """

    customer_name: str | None = None
    phone_number: str | None = None
    qid: str | None = None

    @field_validator(
        "customer_name",
        "phone_number",
        "qid",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

        return value


class MechanicCustomerResponse(BaseModel):
    id: int
    customer_name: str | None
    phone_number: str | None
    qid: str | None


# ==========================================================
# ITEM
# ==========================================================

class MechanicItemCreate(BaseModel):
    """
    One item belonging to a mechanic invoice.
    """

    description: str = Field(
        min_length=1,
        max_length=500,
    )

    quantity: Decimal = Field(
        gt=0,
    )

    unit_price: Decimal = Field(
        ge=0,
    )

    commission: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Item description is required."
            )

        return value


class MechanicItemUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing mechanic invoice item.
    """

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    quantity: Decimal | None = Field(
        default=None,
        gt=0,
    )

    unit_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    commission: Decimal | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError(
                    "Item description is required."
                )

        return value


class MechanicItemResponse(BaseModel):
    id: int
    invoice_id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal


# ==========================================================
# INVOICE
# ==========================================================

class MechanicInvoiceCreate(BaseModel):
    """
    Complete request for creating a mechanic invoice.

    Customer + invoice + items are submitted together.
    """

    customer: MechanicCustomerCreate

    plate_number: str = Field(
        min_length=1,
        max_length=50,
    )

    labor_charges: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    payment_status: PaymentStatus = (
        PaymentStatus.UNPAID
    )

    items: list[MechanicItemCreate] = Field(
        default_factory=list,
    )

    @field_validator("plate_number")
    @classmethod
    def validate_plate_number(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Plate number is required."
            )

        return value


class MechanicInvoiceUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing mechanic invoice.

    customer_id is intentionally excluded because an
    invoice should not be moved to another customer
    through a normal update.
    """

    plate_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    labor_charges: Decimal | None = Field(
        default=None,
        ge=0,
    )

    payment_status: PaymentStatus | None = None

    @field_validator("plate_number")
    @classmethod
    def validate_plate_number(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError(
                    "Plate number is required."
                )

        return value


# ==========================================================
# INVOICE SUMMARY
# ==========================================================

class MechanicInvoiceSummaryResponse(BaseModel):
    """
    Lightweight customer + invoice information used by
    the invoice listing screen.

    No items are included here.
    """

    customer_id: int
    name: str | None
    phone_number: str | None

    invoice_id: int
    plate_number: str
    payment_status: PaymentStatus
    invoice_date: datetime


class MechanicInvoiceSummaryListResponse(BaseModel):
    """
    Paginated list of mechanic invoice summaries.
    """

    customers: list[MechanicInvoiceSummaryResponse]
    pagination: PaginationResponse


# ==========================================================
# FULL INVOICE RESPONSE
# ==========================================================

class MechanicInvoiceResponse(BaseModel):
    """
    Complete mechanic invoice response.

    Includes:

        Customer
        Invoice
        Items

    Mechanic invoices do not contain images.
    """

    id: int
    customer_id: int
    plate_number: str
    labor_charges: Decimal
    payment_status: PaymentStatus
    created_by: int
    created_at: datetime

    customer: MechanicCustomerResponse
    items: list[MechanicItemResponse]