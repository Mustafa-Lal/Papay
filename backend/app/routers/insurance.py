from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota, require_image_quota
from app.models.access_key import AccessKey
from app.schemas.insurance_invoice import (
    InsuranceCustomerUpdate,
    InsuranceInvoiceCreate,
    InsuranceInvoiceResponse,
    InsuranceInvoiceSummaryListResponse,
    InsuranceInvoiceUpdate,
    InsuranceItemUpdate,
    InsuranceItemCreate,
    InsuranceImageResponse,
)
from app.schemas.insurance_finance import (
    InsuranceExpenseCreate,
    InsuranceExpenseListResponse,
    InsuranceExpenseResponse,
    InsuranceExpenseUpdate,
    InsuranceFinanceReportResponse,
    InsuranceIncomeCreate,
    InsuranceIncomeListResponse,
    InsuranceIncomeResponse,
    InsuranceIncomeUpdate,
)
from app.services.insurance_customer_update import update_customer
from app.services.insurance_invoice_by_plate_fetch import get_insurance_invoices_by_plate
from app.services.insurance_invoice_creation import InsuranceItemData, create_insurance_invoice_transaction
from app.services.insurance_invoice_deletion import delete_insurance_invoice
from app.services.insurance_invoice_details_fetch import get_insurance_invoice_full_details
from app.services.insurance_invoice_summary_fetch import get_insurance_customers
from app.services.insurance_invoice_update import update_insurance_invoice
from app.services.insurance_item_update import update_insurance_item
from app.services.insurance_item import create_insurance_item
from app.services.insurance_item_deletion import delete_insurance_item
from app.services.insurance_image_deletion import delete_insurance_image
from app.services.image_fetch import get_insurance_image
from app.services.insurance_image import create_insurance_image
from app.services.insurance_expense import (
    create_insurance_expense,
    deactivate_insurance_expense,
    get_insurance_expenses,
    update_insurance_expense,
)
from app.services.insurance_income import (
    create_insurance_income,
    deactivate_insurance_income,
    get_insurance_incomes,
    update_insurance_income,
)
from app.services.insurance_finance_report import get_insurance_finance_report
from app.models.insurance_image import InsuranceImageType

router = APIRouter(prefix="/insurance")


# ---------------------------------------------------------
# INVOICE ENDPOINTS
# ---------------------------------------------------------

@router.post(
    "/invoices",
    response_model=InsuranceInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_endpoint(
    payload: InsuranceInvoiceCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        items_data = [
            InsuranceItemData(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                commission=item.commission,
            )
            for item in payload.items
        ]

        result = create_insurance_invoice_transaction(
            db=db,
            customer_name=payload.customer.customer_name,
            phone_number=payload.customer.phone_number,
            qid=payload.customer.qid,
            plate_number=payload.plate_number,
            labor_charges=payload.labor_charges,
            payment_status=payload.payment_status,
            created_by=current_access_key.id,
            items=items_data,
        )
        
        # The creation transaction returns a dataclass.
        # We need to fetch the full details for the response.
        return get_insurance_invoice_full_details(db, result.invoice.id)
        
    except ValueError as error:
        # Transaction is rolled back inside the service
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/invoices", response_model=InsuranceInvoiceSummaryListResponse)
def list_invoices_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    plate_number: str | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        if plate_number:
            result = get_insurance_invoices_by_plate(
                db=db,
                plate_number=plate_number,
                limit=limit,
                offset=offset,
            )
            # Adapt the result format to match InsuranceInvoiceSummaryListResponse
            # By Plate returns "invoices" with "customer_name" instead of "name"
            adapted_customers = []
            for inv in result["invoices"]:
                inv["name"] = inv.pop("customer_name")
                adapted_customers.append(inv)
            return {"customers": adapted_customers, "pagination": result["pagination"]}
        else:
            return get_insurance_customers(
                db=db,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
            )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/invoices/{invoice_id}", response_model=InsuranceInvoiceResponse)
def get_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    result = get_insurance_invoice_full_details(db=db, invoice_id=invoice_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )
    return result


@router.put("/invoices/{invoice_id}")
def update_invoice_endpoint(
    invoice_id: int,
    payload: InsuranceInvoiceUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        invoice = update_insurance_invoice(
            db=db,
            invoice_id=invoice_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(invoice)
        # We can just return the detail view
        return get_insurance_invoice_full_details(db=db, invoice_id=invoice_id)
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance invoice not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_insurance_invoice(db=db, invoice_id=invoice_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# CUSTOMER ENDPOINTS
# ---------------------------------------------------------

@router.put("/customers/{customer_id}")
def update_customer_endpoint(
    customer_id: int,
    payload: InsuranceCustomerUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        customer = update_customer(
            db=db,
            customer_id=customer_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(customer)
        return {
            "id": customer.id,
            "customer_name": customer.customer_name,
            "phone_number": customer.phone_number,
            "qid": customer.qid,
        }
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance customer not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# ITEM ENDPOINTS
# ---------------------------------------------------------

@router.post(
    "/invoices/{invoice_id}/items",
    status_code=status.HTTP_201_CREATED,
)
def create_item_endpoint(
    invoice_id: int,
    payload: InsuranceItemCreate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        item = create_insurance_item(
            db=db,
            invoice_id=invoice_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(item)
        return {
            "id": item.id,
            "invoice_id": item.invoice_id,
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "commission": item.commission,
        }
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance invoice does not exist."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put("/items/{item_id}")
def update_item_endpoint(
    item_id: int,
    payload: InsuranceItemUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        item = update_insurance_item(
            db=db,
            item_id=item_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(item)
        return {
            "id": item.id,
            "invoice_id": item.invoice_id,
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "commission": item.commission,
        }
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance item not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_insurance_item(db=db, item_id=item_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# IMAGE ENDPOINTS
# ---------------------------------------------------------

@router.post(
    "/invoices/{invoice_id}/images",
    response_model=InsuranceImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_image_endpoint(
    invoice_id: int,
    image_type: Annotated[InsuranceImageType, Form()],
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
    _img_quota: None = Depends(require_image_quota),
):
    try:
        image_bytes = file.file.read()
        
        image_record = create_insurance_image(
            db=db,
            invoice_id=invoice_id,
            image_type=image_type,
            image_bytes=image_bytes,
        )
        
        return {
            "id": image_record.id,
            "invoice_id": image_record.invoice_id,
            "image_type": image_record.image_type,
            "file_path": image_record.file_path,
        }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance invoice does not exist."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/images/{image_id}")
def get_image_endpoint(
    image_id: int,
    db: Session = Depends(get_db),
    # It might be good to protect image access, but based on the design 
    # we'll assume it's protected just like other routes unless specified otherwise.
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        file_path = get_insurance_image(db=db, image_id=image_id)
        return FileResponse(file_path, media_type="image/jpeg")
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image_endpoint(
    image_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_insurance_image(db=db, image_id=image_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# INSURANCE EXPENSE & INCOME ENDPOINTS
# ---------------------------------------------------------

@router.post(
    "/expenses",
    response_model=InsuranceExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_insurance_expense_endpoint(
    payload: InsuranceExpenseCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        expense = create_insurance_expense(
            db=db,
            description=payload.description,
            price=payload.price,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(expense)
        return expense
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/expenses",
    response_model=InsuranceExpenseListResponse,
)
def list_insurance_expenses_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_insurance_expenses(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put(
    "/expenses/{expense_id}",
    response_model=InsuranceExpenseResponse,
)
def update_insurance_expense_endpoint(
    expense_id: int,
    payload: InsuranceExpenseUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        expense = update_insurance_expense(
            db=db,
            expense_id=expense_id,
            description=payload.description,
            price=payload.price,
        )
        db.commit()
        db.refresh(expense)
        return expense
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance expense not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/expenses/{expense_id}",
    response_model=InsuranceExpenseResponse,
)
def delete_insurance_expense_endpoint(
    expense_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        expense = deactivate_insurance_expense(
            db=db,
            expense_id=expense_id,
        )
        db.commit()
        db.refresh(expense)
        return expense
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance expense not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/incomes",
    response_model=InsuranceIncomeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_insurance_income_endpoint(
    payload: InsuranceIncomeCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        income = create_insurance_income(
            db=db,
            description=payload.description,
            price=payload.price,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(income)
        return income
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/incomes",
    response_model=InsuranceIncomeListResponse,
)
def list_insurance_incomes_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_insurance_incomes(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put(
    "/incomes/{income_id}",
    response_model=InsuranceIncomeResponse,
)
def update_insurance_income_endpoint(
    income_id: int,
    payload: InsuranceIncomeUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        income = update_insurance_income(
            db=db,
            income_id=income_id,
            description=payload.description,
            price=payload.price,
        )
        db.commit()
        db.refresh(income)
        return income
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance income not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/incomes/{income_id}",
    response_model=InsuranceIncomeResponse,
)
def delete_insurance_income_endpoint(
    income_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        income = deactivate_insurance_income(
            db=db,
            income_id=income_id,
        )
        db.commit()
        db.refresh(income)
        return income
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Insurance income not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# INSURANCE FINANCE REPORT ENDPOINT
# ---------------------------------------------------------

@router.get(
    "/report",
    response_model=InsuranceFinanceReportResponse,
)
def get_insurance_finance_report_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    """
    Return a complete finance report for the given date range.

    Combines all active expenses and incomes into a single payload with
    pre-computed totals. No pagination — returns every record so the
    frontend can render a full printable report.

    - start_date / end_date are both optional (ISO-8601 date strings).
    - Omitting both returns all records ever created.
    - Returns 400 if start_date is after end_date.
    """
    try:
        return get_insurance_finance_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
