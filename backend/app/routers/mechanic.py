from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.models.access_key import AccessKey
from app.schemas.mechanic_invoice import (
    MechanicCustomerUpdate,
    MechanicInvoiceCreate,
    MechanicInvoiceResponse,
    MechanicInvoiceSummaryListResponse,
    MechanicInvoiceUpdate,
    MechanicItemUpdate,
    MechanicItemCreate,
)
from app.services.mechanic_customer_update import update_mechanic_customer
from app.services.mechanic_invoice_by_plate_fetch import get_mechanic_invoices_by_plate
from app.services.mechanic_invoice_creation import create_mechanic_invoice_transaction
from app.services.mechanic_invoice_deletion import delete_mechanic_invoice
from app.services.mechanic_invoice_details_fetch import get_mechanic_invoice_full_details
from app.services.mechanic_invoice_summary_fetch import get_mechanic_customers
from app.services.mechanic_invoice_update import update_mechanic_invoice
from app.services.mechanic_item_update import update_mechanic_item
from app.services.mechanic_item import create_mechanic_item
from app.services.mechanic_item_deletion import delete_mechanic_item

router = APIRouter(prefix="/mechanic")


# ---------------------------------------------------------
# INVOICE ENDPOINTS
# ---------------------------------------------------------

@router.post(
    "/invoices",
    response_model=MechanicInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_endpoint(
    payload: MechanicInvoiceCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
):
    try:
        items_data = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "commission": item.commission,
            }
            for item in payload.items
        ]

        result = create_mechanic_invoice_transaction(
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
        
        # We need to fetch the full details for the response.
        return get_mechanic_invoice_full_details(db, result.id)
        
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/invoices", response_model=MechanicInvoiceSummaryListResponse)
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
            result = get_mechanic_invoices_by_plate(
                db=db,
                plate_number=plate_number,
                limit=limit,
                offset=offset,
            )
            # Adapt the result format
            adapted_customers = []
            for inv in result["invoices"]:
                inv["name"] = inv.pop("customer_name")
                adapted_customers.append(inv)
            return {"customers": adapted_customers, "pagination": result["pagination"]}
        else:
            return get_mechanic_customers(
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


@router.get("/invoices/{invoice_id}", response_model=MechanicInvoiceResponse)
def get_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    result = get_mechanic_invoice_full_details(db=db, invoice_id=invoice_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )
    return result


@router.put("/invoices/{invoice_id}")
def update_invoice_endpoint(
    invoice_id: int,
    payload: MechanicInvoiceUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        invoice = update_mechanic_invoice(
            db=db,
            invoice_id=invoice_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(invoice)
        return get_mechanic_invoice_full_details(db=db, invoice_id=invoice_id)
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Mechanic invoice not found."
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
        delete_mechanic_invoice(db=db, invoice_id=invoice_id)
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
    payload: MechanicCustomerUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        customer = update_mechanic_customer(
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
            if str(error) == "Mechanic customer not found."
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
    payload: MechanicItemCreate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        item = create_mechanic_item(
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
            if str(error) == "Mechanic invoice does not exist."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put("/items/{item_id}")
def update_item_endpoint(
    item_id: int,
    payload: MechanicItemUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        item = update_mechanic_item(
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
            if str(error) == "Mechanic item not found."
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
        delete_mechanic_item(db=db, item_id=item_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
