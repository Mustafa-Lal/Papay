import unittest
from datetime import datetime
from decimal import Decimal

from pydantic import ValidationError

from app.schemas.product import (
    PaginationResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)


class ProductSchemaTests(unittest.TestCase):

    # ---------------------------------------------------------
    # PRODUCT CREATE
    # ---------------------------------------------------------

    def test_valid_product_create(self):

        product = ProductCreate(
            description="Engine Oil",
            quantity=Decimal("5.00"),
            unit_price=Decimal("50.00"),
        )

        self.assertEqual(
            product.description,
            "Engine Oil",
        )

        self.assertEqual(
            product.quantity,
            Decimal("5.00"),
        )

        self.assertEqual(
            product.unit_price,
            Decimal("50.00"),
        )

    # ---------------------------------------------------------
    # EMPTY DESCRIPTION
    # ---------------------------------------------------------

    def test_empty_description_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductCreate(
                description="",
                quantity=Decimal("5.00"),
                unit_price=Decimal("50.00"),
            )

    # ---------------------------------------------------------
    # NEGATIVE QUANTITY
    # ---------------------------------------------------------

    def test_negative_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductCreate(
                description="Engine Oil",
                quantity=Decimal("-1.00"),
                unit_price=Decimal("50.00"),
            )

    # ---------------------------------------------------------
    # ZERO QUANTITY
    # ---------------------------------------------------------

    def test_zero_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductCreate(
                description="Engine Oil",
                quantity=Decimal("0.00"),
                unit_price=Decimal("50.00"),
            )

    # ---------------------------------------------------------
    # NEGATIVE UNIT PRICE
    # ---------------------------------------------------------

    def test_negative_unit_price_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductCreate(
                description="Engine Oil",
                quantity=Decimal("5.00"),
                unit_price=Decimal("-50.00"),
            )

    # ---------------------------------------------------------
    # ZERO UNIT PRICE
    # ---------------------------------------------------------

    def test_zero_unit_price_is_allowed(self):

        product = ProductCreate(
            description="Free Item",
            quantity=Decimal("1.00"),
            unit_price=Decimal("0.00"),
        )

        self.assertEqual(
            product.unit_price,
            Decimal("0.00"),
        )

    # ---------------------------------------------------------
    # DESCRIPTION TOO LONG
    # ---------------------------------------------------------

    def test_description_over_500_characters_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductCreate(
                description="A" * 501,
                quantity=Decimal("1.00"),
                unit_price=Decimal("10.00"),
            )

    # ---------------------------------------------------------
    # PRODUCT UPDATE
    # ---------------------------------------------------------

    def test_valid_partial_product_update(self):

        product = ProductUpdate(
            unit_price=Decimal("75.00"),
        )

        self.assertIsNone(
            product.description
        )

        self.assertIsNone(
            product.quantity
        )

        self.assertEqual(
            product.unit_price,
            Decimal("75.00"),
        )

    # ---------------------------------------------------------
    # FULL PRODUCT UPDATE
    # ---------------------------------------------------------

    def test_full_product_update(self):

        product = ProductUpdate(
            description="Updated Engine Oil",
            quantity=Decimal("10.00"),
            unit_price=Decimal("75.00"),
        )

        self.assertEqual(
            product.description,
            "Updated Engine Oil",
        )

        self.assertEqual(
            product.quantity,
            Decimal("10.00"),
        )

        self.assertEqual(
            product.unit_price,
            Decimal("75.00"),
        )

    # ---------------------------------------------------------
    # INVALID UPDATE QUANTITY
    # ---------------------------------------------------------

    def test_negative_update_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductUpdate(
                quantity=Decimal("-1.00"),
            )

    # ---------------------------------------------------------
    # INVALID UPDATE PRICE
    # ---------------------------------------------------------

    def test_negative_update_price_is_rejected(self):

        with self.assertRaises(ValidationError):

            ProductUpdate(
                unit_price=Decimal("-10.00"),
            )

    # ---------------------------------------------------------
    # EMPTY UPDATE
    # ---------------------------------------------------------

    def test_empty_product_update_is_allowed(self):

        product = ProductUpdate()

        self.assertIsNone(
            product.description
        )

        self.assertIsNone(
            product.quantity
        )

        self.assertIsNone(
            product.unit_price
        )

    # ---------------------------------------------------------
    # PRODUCT RESPONSE
    # ---------------------------------------------------------

    def test_valid_product_response(self):

        product = ProductResponse(
            id=1,
            description="Engine Oil",
            quantity=Decimal("5.00"),
            unit_price=Decimal("50.00"),
            created_at=datetime(
                2026,
                8,
                19,
                10,
                30,
            ),
        )

        self.assertEqual(
            product.id,
            1,
        )

        self.assertEqual(
            product.description,
            "Engine Oil",
        )

        self.assertEqual(
            product.quantity,
            Decimal("5.00"),
        )

        self.assertEqual(
            product.unit_price,
            Decimal("50.00"),
        )

    # ---------------------------------------------------------
    # PAGINATION RESPONSE
    # ---------------------------------------------------------

    def test_valid_pagination_response(self):

        pagination = PaginationResponse(
            limit=10,
            offset=0,
            total=25,
            has_more=True,
        )

        self.assertEqual(
            pagination.limit,
            10,
        )

        self.assertEqual(
            pagination.offset,
            0,
        )

        self.assertEqual(
            pagination.total,
            25,
        )

        self.assertTrue(
            pagination.has_more
        )

    # ---------------------------------------------------------
    # PRODUCT LIST RESPONSE
    # ---------------------------------------------------------

    def test_valid_product_list_response(self):

        product = ProductResponse(
            id=1,
            description="Engine Oil",
            quantity=Decimal("5.00"),
            unit_price=Decimal("50.00"),
            created_at=datetime(
                2026,
                8,
                19,
                10,
                30,
            ),
        )

        pagination = PaginationResponse(
            limit=10,
            offset=0,
            total=1,
            has_more=False,
        )

        response = ProductListResponse(
            products=[product],
            pagination=pagination,
        )

        self.assertEqual(
            len(response.products),
            1,
        )

        self.assertEqual(
            response.products[0].id,
            1,
        )

        self.assertEqual(
            response.pagination.total,
            1,
        )

        self.assertFalse(
            response.pagination.has_more
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )