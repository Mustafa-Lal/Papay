from app.database import engine
from app.models.base import Base

from app.models.role import Role
from app.models.access_key import AccessKey
from app.models.session import Session
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.models.insurance_image import InsuranceImage
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem
from app.models.rent import Rent
from app.models.utility_bill import UtilityBill
from app.models.salary import Salary
from app.models.product import Product
from app.models.expense import Expense
from app.models.profit import Profit

with engine.begin() as conn:
    for table in reversed(Base.metadata.sorted_tables):
        conn.execute(table.delete())

print("Database emptied successfully.")
