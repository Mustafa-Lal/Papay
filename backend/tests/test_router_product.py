import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.product import Product


def mock_get_current_access_key() -> AccessKey:
    """Mock the current access key dependency to avoid needing real tokens."""
    return AccessKey(id=1, role_id=1, active=True)


class RouterProductTests(unittest.TestCase):
    def setUp(self):
        # Override the auth dependency for all tests
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup_products()

    def tearDown(self):
        # Clean up dependency overrides and database
        app.dependency_overrides.clear()
        self.cleanup_products()

    def cleanup_products(self):
        with Session(engine) as db:
            products = db.scalars(select(Product)).all()
            for product in products:
                db.delete(product)
            db.commit()

    # ---------------------------------------------------------
    # POST /products
    # ---------------------------------------------------------

    def test_create_product_successfully(self):
        payload = {
            "description": "Brake Pad",
            "quantity": 20,
            "unit_price": 150
        }

        response = self.client.post("/products", json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["description"], "Brake Pad")
        self.assertEqual(data["quantity"], "20.00")
        self.assertEqual(data["unit_price"], "150.00")

    def test_create_product_validation_error(self):
        payload = {
            "description": "",
            "quantity": 0,
            "unit_price": -10
        }

        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    # ---------------------------------------------------------
    # GET /products
    # ---------------------------------------------------------

    def test_list_products(self):
        # Create some products first
        self.client.post("/products", json={"description": "Prod 1", "quantity": 10, "unit_price": 100})
        self.client.post("/products", json={"description": "Prod 2", "quantity": 5, "unit_price": 50})

        response = self.client.get("/products?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["products"]), 2)

    def test_list_products_invalid_limit(self):
        response = self.client.get("/products?limit=0")
        self.assertEqual(response.status_code, 422) # FastAPI validation error for Query(ge=1)

    # ---------------------------------------------------------
    # PUT /products/{product_id}
    # ---------------------------------------------------------

    def test_update_product(self):
        # Create product
        create_res = self.client.post("/products", json={"description": "Old Desc", "quantity": 10, "unit_price": 100})
        product_id = create_res.json()["id"]

        # Update product
        update_payload = {
            "description": "New Desc",
            "quantity": 15,
            "unit_price": 120
        }
        update_res = self.client.put(f"/products/{product_id}", json=update_payload)
        self.assertEqual(update_res.status_code, 200)
        
        data = update_res.json()
        self.assertEqual(data["description"], "New Desc")
        self.assertEqual(data["quantity"], "15.00")
        self.assertEqual(data["unit_price"], "120.00")

    def test_update_nonexistent_product(self):
        update_payload = {"description": "New Desc", "quantity": 15, "unit_price": 120}
        response = self.client.put("/products/9999", json=update_payload)
        self.assertEqual(response.status_code, 404)

    # ---------------------------------------------------------
    # DELETE /products/{product_id}
    # ---------------------------------------------------------

    def test_delete_product(self):
        # Create product
        create_res = self.client.post("/products", json={"description": "To Delete", "quantity": 10, "unit_price": 100})
        product_id = create_res.json()["id"]

        # Delete product
        delete_res = self.client.delete(f"/products/{product_id}")
        self.assertEqual(delete_res.status_code, 204)

        # Verify it doesn't appear in list
        list_res = self.client.get("/products")
        self.assertEqual(list_res.json()["pagination"]["total"], 0)

    def test_delete_nonexistent_product(self):
        response = self.client.delete("/products/9999")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
