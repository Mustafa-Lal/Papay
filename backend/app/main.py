from fastapi import FastAPI

from app.routers import insurance


app = FastAPI(
    title="Papay Garage API",
)


app.include_router(
    insurance.router,
    prefix="/insurance",
    tags=["Insurance"],
)