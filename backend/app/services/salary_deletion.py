from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.salary import Salary


def delete_salary(
    db: Session,
    salary_id: int,
) -> None:

    # --------------------------------------------------
    # Find salary
    # --------------------------------------------------

    salary = db.scalar(
        select(Salary).where(
            Salary.id == salary_id
        )
    )

    if salary is None:
        raise ValueError(
            "Salary not found."
        )

    # --------------------------------------------------
    # Delete salary
    # --------------------------------------------------

    db.delete(salary)