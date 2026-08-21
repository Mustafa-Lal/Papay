from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.schemas.salary import (
    SalaryCreate,
    SalaryListResponse,
    SalaryResponse,
    SalaryUpdate,
)
from app.services.salary import create_salary
from app.services.salary_deletion import delete_salary
from app.services.salary_fetch import get_salaries
from app.services.salary_update import update_salary

router = APIRouter(prefix="/salaries")


@router.post(
    "",
    response_model=SalaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_salary_endpoint(
    payload: SalaryCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        salary = create_salary(
            db=db,
            name=payload.name,
            amount=payload.amount,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(salary)
        return salary
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/{year}/{month}", response_model=SalaryListResponse)
def get_salaries_endpoint(
    year: int,
    month: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_salaries(
            db=db,
            year=year,
            month=month,
            limit=limit,
            offset=offset,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put("/{salary_id}", response_model=SalaryResponse)
def update_salary_endpoint(
    salary_id: int,
    payload: SalaryUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        salary = update_salary(
            db=db,
            salary_id=salary_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(salary)
        return salary
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Salary not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{salary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary_endpoint(
    salary_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_salary(db=db, salary_id=salary_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
