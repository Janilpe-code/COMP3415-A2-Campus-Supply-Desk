
from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


class AdditionalTests(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.service = OrderService(
            Path(self.directory.name) / "state.json"
        )

    def test_invalid_product(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "laptop", "quantity": 1}]
            )

    def test_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "notebook", "quantity": 0}]
            )

    def test_invalid_fulfillment(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "notebook", "quantity": 1}],
                "helicopter"
            )

    def test_quote_does_not_reduce_stock(self):
        before = self.service.catalog()

        self.service.quote(
            "regular",
            [{"product_id": "notebook", "quantity": 2}]
        )

        self.assertEqual(self.service.catalog(), before)


    def test_cancelling_twice_does_not_add_extra_stock(self):
        original_stock = next(
            p["stock"] for p in self.service.catalog()
            if p["product_id"] == "notebook"
        )

        order = self.service.place_order(
            "regular",
            [{"product_id": "notebook", "quantity": 2}]
        )

        self.service.cancel_order(order["order_id"])

        # The second cancellation should not restore stock again.
        try:
            self.service.cancel_order(order["order_id"])
        except ValueError:
            pass

        final_stock = next(
            p["stock"] for p in self.service.catalog()
            if p["product_id"] == "notebook"
        )

        self.assertEqual(final_stock, original_stock)

    def test_express_delivery_quote(self):
        quote = self.service.quote(
            "regular",
            [{"product_id": "notebook", "quantity": 2}],
            "express"
        )

        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(quote["total_cents"], 2200)

    def test_express_order_is_saved(self):
        order = self.service.place_order(
            "regular",
            [{"product_id": "notebook", "quantity": 2}],
            "express"
        )

        saved_order = self.service.get_order(order["order_id"])

        self.assertEqual(saved_order["fulfillment"], "express")
        self.assertEqual(saved_order["delivery_cents"], 1200)
        self.assertEqual(saved_order["total_cents"], 2200)

    def test_express_delivery_still_charges_for_large_order(self):
        quote = self.service.quote(
            "regular",
            [{"product_id": "hoodie", "quantity": 3}],
            "express"
        )

        self.assertEqual(quote["subtotal_cents"], 12000)
        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(quote["total_cents"], 13200)

if __name__ == "__main__":
    unittest.main()
