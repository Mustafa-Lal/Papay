"""
Pydantic schemas for insurance invoice API requests and responses.

These schemas define the contract between Flutter and the backend.

Creation follows the insurance invoice hierarchy:

    Customer
        ↓
    Invoice
        ↓
    Items
        ↓
    Images

Customers, invoices, and items can be updated independently after
they have been created.

Images are uploaded and deleted through their invoice/image endpoints.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.insurance_image import InsuranceImageType
from app.models.insurance_invoice import PaymentStatus
from app.schemas.product import PaginationResponse


# ==========================================================
# CUSTOMER
# ==========================================================

class InsuranceCustomerCreate(BaseModel):
    """
    Customer information submitted when creating an invoice.

    Customers are not created through a separate customer
    creation endpoint. They are created as part of the
    insurance invoice creation workflow.
    """

    customer_name: str | None = None
    phone_number: str | None = None
    qid: str | None = None

    @field_validator(
        "customer_name",
        "phone_number",
        "qid",
    )
    @classmethod
    def convert_empty_strings_to_none(cls, value):
        if value is not None:
            value = value.strip()

            if value == "":
                return None

        return value


class InsuranceCustomerUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing insurance customer.
    """

    customer_name: str | None = None
    phone_number: str | None = None
    qid: str | None = None

    @field_validator(
        "customer_name",
        "phone_number",
        "qid",
    )
    @classmethod
    def convert_empty_strings_to_none(cls, value):
        if value is not None:
            value = value.strip()

            if value == "":
                return None

        return value


class InsuranceCustomerResponse(BaseModel):
    """
    Insurance customer returned by the API.
    """

    id: int
    customer_name: str | None
    phone_number: str | None
    qid: str | None


# ==========================================================
# ITEM
# ==========================================================

class InsuranceItemCreate(BaseModel):
    """
    One item belonging to an insurance invoice.

    During invoice creation, items are submitted inside
    InsuranceInvoiceCreate.
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
    def validate_description(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Item description is required."
            )

        return value


class InsuranceItemUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing insurance invoice item.
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


class InsuranceItemResponse(BaseModel):
    """
    Insurance invoice item returned by the API.
    """

    id: int
    invoice_id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal


# ==========================================================
# INVOICE
# ==========================================================

class InsuranceInvoiceCreate(BaseModel):
    """
    Complete request for creating an insurance invoice.

    Customer + invoice + items are submitted together.
    """

    customer: InsuranceCustomerCreate

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

    items: list[InsuranceItemCreate] = Field(
        min_length=1,
    )

    @field_validator("plate_number")
    @classmethod
    def validate_plate_number(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Plate number is required."
            )

        return value


class InsuranceInvoiceUpdate(BaseModel):
    """
    Fields that can be independently updated on an
    existing insurance invoice.

    customer_id is intentionally not included because
    an invoice should not be moved between customers
    through a normal update operation.
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
# IMAGE
# ==========================================================

class InsuranceImageResponse(BaseModel):
    """
    Image metadata returned with a full insurance invoice.

    The actual image file is stored outside the database.
    The API returns the stored file path.
    """

    id: int
    invoice_id: int
    image_type: InsuranceImageType
    file_path: str


# ==========================================================
# INVOICE SUMMARY
# ==========================================================

class InsuranceInvoiceSummaryResponse(BaseModel):
    """
    Lightweight invoice/customer information used for
    invoice listing screens.

    This does NOT contain items or images.
    """

    customer_id: int
    name: str | None
    phone_number: str | None

    invoice_id: int
    plate_number: str
    payment_status: PaymentStatus
    invoice_date: datetime


class InsuranceInvoiceSummaryListResponse(BaseModel):
    """
    Paginated list of insurance invoice summaries.
    """

    customers: list[InsuranceInvoiceSummaryResponse]
    pagination: PaginationResponse


# ==========================================================
# FULL INVOICE RESPONSE
# ==========================================================

class InsuranceInvoiceResponse(BaseModel):
    """
    Complete insurance invoice response.

    Includes:

        Customer
        Invoice
        Items
        Images
    """

    id: int
    customer_id: int
    plate_number: str
    labor_charges: Decimal
    payment_status: PaymentStatus
    created_by: int
    created_at: datetime

    customer: InsuranceCustomerResponse
    items: list[InsuranceItemResponse]
    images: list[InsuranceImageResponse]