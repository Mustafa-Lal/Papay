from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import (
    admin,
    auth,
    expense,
    insurance,
    mechanic,
    product,
    profit,
    rent,
    salary,
    summary,
    utility_bill,
)


app = FastAPI(
    title="Papay Garage API",
)


app.include_router(auth.router, tags=["Auth"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(product.router, tags=["Products"])
app.include_router(insurance.router, tags=["Insurance"])
app.include_router(mechanic.router, tags=["Mechanic"])
app.include_router(rent.router, tags=["Rent"])
app.include_router(utility_bill.router, tags=["Utility Bills"])
app.include_router(salary.router, tags=["Salaries"])
app.include_router(expense.router, tags=["Expenses"])
app.include_router(profit.router, tags=["Profits"])
app.include_router(summary.router)
