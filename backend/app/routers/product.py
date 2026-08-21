from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product import create_product
from app.services.product_deletion import deactivate_product
from app.services.product_fetch import get_products
from app.services.product_update import update_product


router = APIRouter(prefix="/products")


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        product = create_product(
            db=db,
            description=payload.description,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(product)

        return product
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("", response_model=ProductListResponse)
def list_products_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_products(
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


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        product = update_product(
            db=db,
            product_id=product_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(product)

        return product
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Product not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
) -> None:
    try:
        deactivate_product(db=db, product_id=product_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
