from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --------------------------------------------------
# Pagination Schema
# --------------------------------------------------

class InsuranceFinancePaginationResponse(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


# --------------------------------------------------
# Insurance Expense Schemas
# --------------------------------------------------

class InsuranceExpenseCreate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )

    price: Decimal = Field(
        ge=0,
    )


class InsuranceExpenseUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )


class InsuranceExpenseResponse(BaseModel):
    id: int
    description: str
    price: Decimal
    created_at: datetime


class InsuranceExpenseListResponse(BaseModel):
    expenses: list[InsuranceExpenseResponse]
    pagination: InsuranceFinancePaginationResponse


# --------------------------------------------------
# Insurance Income Schemas
# --------------------------------------------------

class InsuranceIncomeCreate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )

    price: Decimal = Field(
        ge=0,
    )


class InsuranceIncomeUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )


class InsuranceIncomeResponse(BaseModel):
    id: int
    description: str
    price: Decimal
    created_at: datetime


class InsuranceIncomeListResponse(BaseModel):
    incomes: list[InsuranceIncomeResponse]
    pagination: InsuranceFinancePaginationResponse
