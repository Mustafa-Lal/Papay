"""
Pydantic schemas for the monthly financial summary endpoint.
"""

from decimal import Decimal

from pydantic import BaseModel


class InvoiceProfitBreakdown(BaseModel):
    """Paid/unpaid split for invoice-sourced profit."""
    total: Decimal
    paid: Decimal
    unpaid: Decimal


class UtilityExpenseBreakdown(BaseModel):
    """Per-type utility bill amounts for the month."""
    INTERNET: Decimal
    ELECTRICITY: Decimal
    WATER: Decimal
    total: Decimal


class SalaryEntry(BaseModel):
    """Individual employee salary entry."""
    name: str
    amount: Decimal


class SalaryExpenseBreakdown(BaseModel):
    """All salary entries for the month with a running total."""
    employees: list[SalaryEntry]
    total: Decimal


class MonthlySummaryResponse(BaseModel):
    """Complete monthly financial snapshot for the owner."""
    year: int
    month: int

    # ── Profit sources ────────────────────────────────────────
    insurance_profit: InvoiceProfitBreakdown
    mechanic_profit: InvoiceProfitBreakdown
    parts_profit: Decimal          # from garage-records "profits" table

    # ── Expense sources ───────────────────────────────────────
    product_expense: Decimal       # qty × unit_price from products
    rent_expense: Decimal          # rent for the month (0 if none entered)
    utility_expense: UtilityExpenseBreakdown
    salary_expense: SalaryExpenseBreakdown
    garage_expense: Decimal        # from garage-records "expenses" table

    # ── Totals ────────────────────────────────────────────────
    total_profit: Decimal
    total_expense: Decimal
    net: Decimal                   # total_profit − total_expense
