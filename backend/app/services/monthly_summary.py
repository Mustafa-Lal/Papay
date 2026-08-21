"""
Monthly financial summary service.

Calculates all profit and expense figures for a given year/month using
aggregate SQL queries — no full row hydration — to keep RAM usage minimal.

Profit rules:
  - Insurance invoices : grand_total = SUM(qty * unit_price + commission) + labor_charges
  - Mechanic invoices  : labor_charges + SUM(commission from items)
  - Parts profit       : SUM(amount) from the profits table (garage records)

Expense rules:
  - Products       : SUM(qty * unit_price) for records created in that month
  - Rent           : amount for the rent row whose year/month match
  - Utility bills  : per-type SUM for rows whose year/month match
  - Salaries       : per-employee entries created in that month
  - Garage expense : SUM(amount) from the expenses table (garage records)

Only invoices with is_active = True are included.
"""

from decimal import Decimal
from datetime import datetime

from sqlalchemy import extract, func, case, select
from sqlalchemy.orm import Session

from app.models.insurance_invoice import InsuranceInvoice, PaymentStatus
from app.models.insurance_item import InsuranceItem
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem
from app.models.product import Product
from app.models.rent import Rent
from app.models.utility_bill import UtilityBill, UtilityBillType
from app.models.salary import Salary
from app.models.expense import Expense
from app.models.profit import Profit
from app.schemas.summary import (
    InvoiceProfitBreakdown,
    MonthlySummaryResponse,
    SalaryEntry,
    SalaryExpenseBreakdown,
    UtilityExpenseBreakdown,
)

_ZERO = Decimal("0.00")


# ─────────────────────────────────────────────────────────────────────────────
# Insurance profit
# ─────────────────────────────────────────────────────────────────────────────

def _insurance_profit(db: Session, year: int, month: int) -> InvoiceProfitBreakdown:
    """
    Grand total per invoice = SUM(qty * unit_price + commission) across its items
                              PLUS the invoice's labor_charges.

    We aggregate in two steps using a sub-select so we avoid loading any rows.
    """
    # Step 1: per-invoice item subtotal
    item_sub = (
        select(
            InsuranceItem.invoice_id,
            func.coalesce(
                func.sum(
                    InsuranceItem.quantity * InsuranceItem.unit_price
                    + InsuranceItem.commission
                ),
                _ZERO,
            ).label("items_total"),
        )
        .where(InsuranceItem.is_active == True)
        .group_by(InsuranceItem.invoice_id)
        .subquery()
    )

    # Step 2: join to invoice, filter by month, aggregate paid/unpaid
    row = db.execute(
        select(
            func.coalesce(func.sum(
                case(
                    (InsuranceInvoice.payment_status == PaymentStatus.PAID,
                     func.coalesce(item_sub.c.items_total, _ZERO)
                     + InsuranceInvoice.labor_charges),
                    else_=_ZERO,
                )
            ), _ZERO).label("paid"),
            func.coalesce(func.sum(
                case(
                    (InsuranceInvoice.payment_status != PaymentStatus.PAID,
                     func.coalesce(item_sub.c.items_total, _ZERO)
                     + InsuranceInvoice.labor_charges),
                    else_=_ZERO,
                )
            ), _ZERO).label("unpaid"),
        )
        .select_from(InsuranceInvoice)
        .outerjoin(item_sub, item_sub.c.invoice_id == InsuranceInvoice.id)
        .where(
            InsuranceInvoice.is_active == True,
            extract("year", InsuranceInvoice.created_at) == year,
            extract("month", InsuranceInvoice.created_at) == month,
        )
    ).one()

    paid = Decimal(str(row.paid or _ZERO))
    unpaid = Decimal(str(row.unpaid or _ZERO))
    return InvoiceProfitBreakdown(total=paid + unpaid, paid=paid, unpaid=unpaid)


# ─────────────────────────────────────────────────────────────────────────────
# Mechanic profit  (labor_charges + commissions only — NOT qty*unit_price)
# ─────────────────────────────────────────────────────────────────────────────

def _mechanic_profit(db: Session, year: int, month: int) -> InvoiceProfitBreakdown:
    """
    Profit from mechanic invoices = labor_charges + SUM(commission from items).
    Parts (qty × unit_price) are NOT profit — they are an expense paid by the customer.
    """
    commission_sub = (
        select(
            MechanicItem.invoice_id,
            func.coalesce(func.sum(MechanicItem.commission), _ZERO).label("commission_total"),
        )
        .group_by(MechanicItem.invoice_id)
        .subquery()
    )

    row = db.execute(
        select(
            func.coalesce(func.sum(
                case(
                    (MechanicInvoice.payment_status == PaymentStatus.PAID,
                     MechanicInvoice.labor_charges
                     + func.coalesce(commission_sub.c.commission_total, _ZERO)),
                    else_=_ZERO,
                )
            ), _ZERO).label("paid"),
            func.coalesce(func.sum(
                case(
                    (MechanicInvoice.payment_status != PaymentStatus.PAID,
                     MechanicInvoice.labor_charges
                     + func.coalesce(commission_sub.c.commission_total, _ZERO)),
                    else_=_ZERO,
                )
            ), _ZERO).label("unpaid"),
        )
        .select_from(MechanicInvoice)
        .outerjoin(commission_sub, commission_sub.c.invoice_id == MechanicInvoice.id)
        .where(
            MechanicInvoice.is_active == True,
            extract("year", MechanicInvoice.created_at) == year,
            extract("month", MechanicInvoice.created_at) == month,
        )
    ).one()

    paid = Decimal(str(row.paid or _ZERO))
    unpaid = Decimal(str(row.unpaid or _ZERO))
    return InvoiceProfitBreakdown(total=paid + unpaid, paid=paid, unpaid=unpaid)


# ─────────────────────────────────────────────────────────────────────────────
# Product expense
# ─────────────────────────────────────────────────────────────────────────────

def _product_expense(db: Session, year: int, month: int) -> Decimal:
    result = db.scalar(
        select(
            func.coalesce(
                func.sum(Product.quantity * Product.unit_price),
                _ZERO,
            )
        ).where(
            Product.is_active == True,
            extract("year", Product.created_at) == year,
            extract("month", Product.created_at) == month,
        )
    )
    return Decimal(str(result or _ZERO))


# ─────────────────────────────────────────────────────────────────────────────
# Rent expense
# ─────────────────────────────────────────────────────────────────────────────

def _rent_expense(db: Session, year: int, month: int) -> Decimal:
    result = db.scalar(
        select(Rent.amount).where(
            Rent.year == year,
            Rent.month == month,
        )
    )
    return Decimal(str(result or _ZERO))


# ─────────────────────────────────────────────────────────────────────────────
# Utility bill expense
# ─────────────────────────────────────────────────────────────────────────────

def _utility_expense(db: Session, year: int, month: int) -> UtilityExpenseBreakdown:
    rows = db.execute(
        select(
            UtilityBill.bill_type,
            func.coalesce(func.sum(UtilityBill.amount), _ZERO).label("amount"),
        )
        .where(UtilityBill.year == year, UtilityBill.month == month)
        .group_by(UtilityBill.bill_type)
    ).all()

    per_type: dict[str, Decimal] = {r.bill_type: Decimal(str(r.amount)) for r in rows}
    internet    = per_type.get(UtilityBillType.INTERNET, _ZERO)
    electricity = per_type.get(UtilityBillType.ELECTRICITY, _ZERO)
    water       = per_type.get(UtilityBillType.WATER, _ZERO)

    return UtilityExpenseBreakdown(
        INTERNET=internet,
        ELECTRICITY=electricity,
        WATER=water,
        total=internet + electricity + water,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Salary expense
# ─────────────────────────────────────────────────────────────────────────────

def _salary_expense(db: Session, year: int, month: int) -> SalaryExpenseBreakdown:
    rows = db.execute(
        select(Salary.name, Salary.amount)
        .where(
            extract("year", Salary.created_at) == year,
            extract("month", Salary.created_at) == month,
        )
        .order_by(Salary.name)
    ).all()

    employees = [SalaryEntry(name=r.name, amount=Decimal(str(r.amount))) for r in rows]
    total = sum((e.amount for e in employees), _ZERO)
    return SalaryExpenseBreakdown(employees=employees, total=total)


# ─────────────────────────────────────────────────────────────────────────────
# Garage expense (from the Expense table — garage records)
# ─────────────────────────────────────────────────────────────────────────────

def _garage_expense(db: Session, year: int, month: int) -> Decimal:
    result = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), _ZERO))
        .where(
            Expense.is_active == True,
            extract("year", Expense.created_at) == year,
            extract("month", Expense.created_at) == month,
        )
    )
    return Decimal(str(result or _ZERO))


# ─────────────────────────────────────────────────────────────────────────────
# Parts profit (from the Profit table — garage records)
# ─────────────────────────────────────────────────────────────────────────────

def _parts_profit(db: Session, year: int, month: int) -> Decimal:
    result = db.scalar(
        select(func.coalesce(func.sum(Profit.amount), _ZERO))
        .where(
            Profit.is_active == True,
            extract("year", Profit.created_at) == year,
            extract("month", Profit.created_at) == month,
        )
    )
    return Decimal(str(result or _ZERO))


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def get_monthly_summary(db: Session, year: int, month: int) -> MonthlySummaryResponse:
    """
    Compute and return the full monthly financial summary.

    All calculations are done via aggregate SQL — no rows are loaded into
    Python memory — keeping this safe for low-RAM environments.
    """
    ins_profit  = _insurance_profit(db, year, month)
    mech_profit = _mechanic_profit(db, year, month)
    parts       = _parts_profit(db, year, month)

    prod_exp    = _product_expense(db, year, month)
    rent_exp    = _rent_expense(db, year, month)
    util_exp    = _utility_expense(db, year, month)
    sal_exp     = _salary_expense(db, year, month)
    gar_exp     = _garage_expense(db, year, month)

    total_profit  = ins_profit.total + mech_profit.total + parts
    total_expense = (
        prod_exp
        + rent_exp
        + util_exp.total
        + sal_exp.total
        + gar_exp
    )

    return MonthlySummaryResponse(
        year=year,
        month=month,
        insurance_profit=ins_profit,
        mechanic_profit=mech_profit,
        parts_profit=parts,
        product_expense=prod_exp,
        rent_expense=rent_exp,
        utility_expense=util_exp,
        salary_expense=sal_exp,
        garage_expense=gar_exp,
        total_profit=total_profit,
        total_expense=total_expense,
        net=total_profit - total_expense,
    )
