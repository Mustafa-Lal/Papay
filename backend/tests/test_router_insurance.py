import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.models.insurance_image import InsuranceImage


def mock_get_current_access_key() -> AccessKey:
    """Mock the current access key dependency to avoid needing real tokens."""
    return AccessKey(id=1, role_id=1, active=True)


class RouterInsuranceTests(unittest.TestCase):
    def setUp(self):
        # Override the auth dependency for all tests
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup_insurance()

    def tearDown(self):
        # Clean up dependency overrides and database
        app.dependency_overrides.clear()
        self.cleanup_insurance()

    def cleanup_insurance(self):
        with Session(engine) as db:
            items = db.scalars(select(InsuranceItem)).all()
            for i in items:
                db.delete(i)
                
            images = db.scalars(select(InsuranceImage)).all()
            for img in images:
                db.delete(img)

            invoices = db.scalars(select(InsuranceInvoice)).all()
            for inv in invoices:
                db.delete(inv)
                
            customers = db.scalars(select(InsuranceCustomer)).all()
            for cus in customers:
                db.delete(cus)
                
            db.commit()

    # ---------------------------------------------------------
    # POST /insurance/invoices
    # ---------------------------------------------------------

    def test_create_insurance_invoice_successfully(self):
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
                    "description": "Bumper Repair",
                    "quantity": 1,
                    "unit_price": 200,
                    "commission": 10
                },
                {
                    "description": "Paint",
                    "quantity": 2,
                    "unit_price": 100,
                    "commission": 0
                }
            ]
        }

        response = self.client.post("/insurance/invoices", json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["plate_number"], "TEST-PLATE")
        self.assertEqual(data["labor_charges"], "500.00")
        
        self.assertEqual(data["customer"]["customer_name"], "Test Customer")
        
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][0]["description"], "Bumper Repair")
        self.assertEqual(data["items"][1]["description"], "Paint")

    def test_create_invoice_validation_error(self):
        payload = {
            "customer": {
                "customer_name": "Test Customer",
                "phone_number": "12345678"
            },
            "plate_number": "", # empty plate number
            "items": [] # empty items
        }

        response = self.client.post("/insurance/invoices", json=payload)
        self.assertEqual(response.status_code, 422)

    # ---------------------------------------------------------
    # GET /insurance/invoices
    # ---------------------------------------------------------

    def test_list_invoices(self):
        # Create some invoices first
        self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "PLATE-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "Cust 2"},
            "plate_number": "PLATE-2",
            "items": [{"description": "Item 2", "quantity": 1, "unit_price": 100}]
        })

        response = self.client.get("/insurance/invoices?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["customers"]), 2)
        
        # Test plate number filter
        response_plate = self.client.get("/insurance/invoices?plate_number=PLATE-1")
        self.assertEqual(response_plate.status_code, 200)
        data_plate = response_plate.json()
        self.assertEqual(data_plate["pagination"]["total"], 1)
        self.assertEqual(data_plate["customers"][0]["plate_number"], "PLATE-1")

    # ---------------------------------------------------------
    # GET /insurance/invoices/{invoice_id}
    # ---------------------------------------------------------

    def test_get_invoice(self):
        # Create invoice
        create_res = self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "PLATE-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]

        get_res = self.client.get(f"/insurance/invoices/{invoice_id}")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.json()
        self.assertEqual(data["plate_number"], "PLATE-1")

    # ---------------------------------------------------------
    # PUT Endpoints
    # ---------------------------------------------------------

    def test_update_invoice(self):
        create_res = self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "Cust 1"},
            "plate_number": "OLD-PLATE",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]
        customer_id = create_res.json()["customer_id"]
        item_id = create_res.json()["items"][0]["id"]

        # Update Invoice
        inv_res = self.client.put(f"/insurance/invoices/{invoice_id}", json={"plate_number": "NEW-PLATE"})
        self.assertEqual(inv_res.status_code, 200)
        self.assertEqual(inv_res.json()["plate_number"], "NEW-PLATE")

        # Update Customer
        cus_res = self.client.put(f"/insurance/customers/{customer_id}", json={"customer_name": "New Cust"})
        self.assertEqual(cus_res.status_code, 200)
        self.assertEqual(cus_res.json()["customer_name"], "New Cust")

        # Update Item
        itm_res = self.client.put(f"/insurance/items/{item_id}", json={"description": "New Item"})
        self.assertEqual(itm_res.status_code, 200)
        self.assertEqual(itm_res.json()["description"], "New Item")

    # ---------------------------------------------------------
    # DELETE Endpoints
    # ---------------------------------------------------------

    def test_delete_invoice(self):
        create_res = self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "To Delete"},
            "plate_number": "DEL-1",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        invoice_id = create_res.json()["id"]

        delete_res = self.client.delete(f"/insurance/invoices/{invoice_id}")
        self.assertEqual(delete_res.status_code, 204)

        get_res = self.client.get(f"/insurance/invoices/{invoice_id}")
        self.assertEqual(get_res.status_code, 404)

    # ---------------------------------------------------------
    # Image Endpoints
    # ---------------------------------------------------------

    def test_image_lifecycle(self):
        # 1. Create Invoice
        create_res = self.client.post("/insurance/invoices", json={
            "customer": {"customer_name": "Image Test"},
            "plate_number": "IMG-123",
            "items": [{"description": "Item 1", "quantity": 1, "unit_price": 100}]
        })
        self.assertEqual(create_res.status_code, 201)
        invoice_id = create_res.json()["id"]

        # Create a tiny valid 1x1 JPEG image in memory
        import io
        from PIL import Image
        
        img_buffer = io.BytesIO()
        img = Image.new('RGB', (1, 1), color='red')
        img.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # 2. Upload Image
        upload_res = self.client.post(
            f"/insurance/invoices/{invoice_id}/images",
            data={"image_type": "BEFORE"},
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        self.assertEqual(upload_res.status_code, 201)
        image_data = upload_res.json()
        self.assertIn("id", image_data)
        self.assertEqual(image_data["image_type"], "BEFORE")
        self.assertEqual(image_data["invoice_id"], invoice_id)
        image_id = image_data["id"]

        # 3. Retrieve Image File
        get_res = self.client.get(f"/insurance/images/{image_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.headers["content-type"], "image/jpeg")

        # 4. Delete Image
        del_res = self.client.delete(f"/insurance/images/{image_id}")
        self.assertEqual(del_res.status_code, 204)

        # 5. Verify Deletion
        get_deleted_res = self.client.get(f"/insurance/images/{image_id}")
        self.assertEqual(get_deleted_res.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
