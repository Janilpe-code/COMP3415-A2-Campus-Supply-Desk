
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


if __name__ == "__main__":
    unittest.main()
