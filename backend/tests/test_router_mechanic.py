import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem


def mock_get_current_access_key() -> AccessKey:
    """Mock the current access key dependency to avoid needing real tokens."""
    return AccessKey(id=1, role_id=1, active=True)


class RouterMechanicTests(unittest.TestCase):
    def setUp(self):
        # Override the auth dependency for all tests
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup_mechanic()

    def tearDown(self):
        # Clean up dependency overrides and database
        app.dependency_overrides.clear()
        self.cleanup_mechanic()

    def cleanup_mechanic(self):
        with Session(engine) as db:
            items = db.scalars(select(MechanicItem)).all()
            for i in items:
                db.delete(i)

            invoices = db.scalars(select(MechanicInvoice)).all()
            for inv in invoices:
                db.delete(inv)
                
            customers = db.scalars(select(MechanicCustomer)).all()
            for cus in customers:
                db.delete(cus)
                
            db.commit()

    # ---------------------------------------------------------
    # POST /mechanic/invoices
    # ---------------------------------------------------------

    def test_create_mechanic_invoice_successfully(self):
        payload = {
            "customer": {
                "customer_name": "Test Customer",
                "phone_number": "12345678",
                "qid": "QID123"
            },
            "plate_number": "TEST-PLATE",
            "labor_charges": 500,
            "payment_status": "PAID",
            "items": [
                {
                    "description": "Oil Change",
                    "quantity": 1,
                    "unit_price": 200,
                    "commission": 10
                },
                {
                    "description": "Filter",
                    "quantity": 2,
                    "unit_price": 100,
                    "commission": 0
                }
            ]
        }

        response = self.client.post("/mechanic/invoices", json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["plate_number"], "TEST-PLATE")
        self.assertEqual(data["labor_charges"], "500.00")
        
        self.assertEqual(data["customer"]["customer_name"], "Test Customer")
        
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][0]["description"], "Oil Change")
        self.assertEqual(data["items"][1]["description"], "Filter")

    def test_create_invoice_validation_error(self):
        payload = {
            "customer": {
                "customer_name": "Test Customer",
                "phone_number": "12345678"
            },
            "plate_number": "", # empty plate number
            "items": [] # empty items
        }

        response = self.client.post("/mechanic/invoices", json=payload)
        self.assertEqual(response.status_code, 422)

    # ---------------------------------------------------------
    # GET /mechanic/invoices
    # ---------------------------------------------------------

    def test_list_invoices(self):
        # Create some invoices first
        self.client.post("/mechanic/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "PLATE-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        self.client.post("/mechanic/invoices", json={
            "customer": {"customer_name": "Cust 2"},
            "plate_number": "PLATE-2",
            "items": [{"description": "Item 2", "quantity": 1, "unit_price": 100}]
        })

        response = self.client.get("/mechanic/invoices?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["customers"]), 2)
        
        # Test plate number filter
        response_plate = self.client.get("/mechanic/invoices?plate_number=PLATE-1")
        self.assertEqual(response_plate.status_code, 200)
        data_plate = response_plate.json()
        self.assertEqual(data_plate["pagination"]["total"], 1)
        self.assertEqual(data_plate["customers"][0]["plate_number"], "PLATE-1")

    # ---------------------------------------------------------
    # GET /mechanic/invoices/{invoice_id}
    # ---------------------------------------------------------

    def test_get_invoice(self):
        # Create invoice
        create_res = self.client.post("/mechanic/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "PLATE-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]

        get_res = self.client.get(f"/mechanic/invoices/{invoice_id}")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.json()
        self.assertEqual(data["plate_number"], "PLATE-1")

    # ---------------------------------------------------------
    # PUT Endpoints
    # ---------------------------------------------------------

    def test_update_invoice(self):
        create_res = self.client.post("/mechanic/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "OLD-PLATE",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]
        customer_id = create_res.json()["customer_id"]
        item_id = create_res.json()["items"][0]["id"]

        # Update Invoice
        inv_res = self.client.put(f"/mechanic/invoices/{invoice_id}", json={"plate_number": "NEW-PLATE"})
        self.assertEqual(inv_res.status_code, 200)
        self.assertEqual(inv_res.json()["plate_number"], "NEW-PLATE")

        # Update Customer
        cus_res = self.client.put(f"/mechanic/customers/{customer_id}", json={"customer_name": "New Cust"})
        self.assertEqual(cus_res.status_code, 200)
        self.assertEqual(cus_res.json()["customer_name"], "New Cust")

        # Update Item
        itm_res = self.client.put(f"/mechanic/items/{item_id}", json={"description": "New Item"})
        self.assertEqual(itm_res.status_code, 200)
        self.assertEqual(itm_res.json()["description"], "New Item")

    # ---------------------------------------------------------
    # DELETE Endpoints
    # ---------------------------------------------------------

    def test_delete_invoice(self):
        create_res = self.client.post("/mechanic/invoices", json={
            "customer": {"customer_name": "To Delete"},
            "plate_number": "DEL-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]

        delete_res = self.client.delete(f"/mechanic/invoices/{invoice_id}")
        self.assertEqual(delete_res.status_code, 204)

        get_res = self.client.get(f"/mechanic/invoices/{invoice_id}")
        self.assertEqual(get_res.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
