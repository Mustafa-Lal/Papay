from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# Pagination
# --------------------------------------------------

class PaginationResponse(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


# --------------------------------------------------
# Product Create
# --------------------------------------------------

class ProductCreate(BaseModel):
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


# --------------------------------------------------
# Product Update
# --------------------------------------------------

class ProductUpdate(BaseModel):
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


# --------------------------------------------------
# Product Response
# --------------------------------------------------

class ProductResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    created_at: datetime


# --------------------------------------------------
# Product List Response
# --------------------------------------------------

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    pagination: PaginationResponse