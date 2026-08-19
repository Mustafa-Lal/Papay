from app.database import engine
from app.models.profit import Profit


with engine.begin() as connection:
    Profit.__table__.drop(
        connection,
        checkfirst=True,
    )

print("profits table dropped.")