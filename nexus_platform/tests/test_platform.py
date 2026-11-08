"""Automated integration test suite for Nexus Inventory Platform."""

import os
import unittest
from pathlib import Path
import tempfile

from nexus_platform.app.database import DatabaseSession, init_db
from nexus_platform.app.services import auth, users, products, warehouse, inventory, orders, reporting, events
from nexus_platform.app.migrations.runner import run_migrations


class TestNexusPlatform(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_nexus.db"
        init_db(self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_auth_token_lifecycle(self):
        token = auth.generate_token("alice_admin", role="admin")
        self.assertIsNotNone(token)
        verified = auth.verify_token(token)
        self.assertIsNotNone(verified)
        self.assertEqual(verified["username"], "alice_admin")
        self.assertEqual(verified["role"], "admin")

    def test_end_to_end_order_flow(self):
        with DatabaseSession(self.db_path) as db:
            # 1. Create User
            user = users.create_user(db, "bob_dev", "bob@nexus.internal")
            self.assertEqual(user["username"], "bob_dev")

            # 2. Create Product
            prod = products.create_product(db, "SKU-990", "Enterprise Server", 1250.00, "Hardware")
            self.assertEqual(prod["sku"], "SKU-990")

            # 3. Create Warehouse
            wh = warehouse.create_warehouse(db, "WH-EAST-1", "Virginia Logistics Hub", "Ashburn, VA", 50000)
            self.assertEqual(wh["code"], "WH-EAST-1")

            # 4. Allocate Inventory
            inv = inventory.set_inventory(db, prod["id"], wh["id"], quantity=10)
            self.assertEqual(inv["quantity"], 10)

            # 5. Place Valid Order
            order = orders.create_order(db, user["id"], prod["id"], wh["id"], quantity=4)
            self.assertEqual(order["status"], "confirmed")
            self.assertEqual(order["total_amount"], 5000.00)

            # Check reserved stock
            stock = inventory.get_stock_level(db, prod["id"], wh["id"])
            self.assertEqual(stock["reserved"], 4)
            self.assertEqual(stock["available"], 6)

            # Check domain events
            evts = events.list_events(db, "ORDER_PLACED")
            self.assertEqual(len(evts), 1)
            self.assertEqual(evts[0]["payload"]["order_id"], order["order_id"])

            # Check sales summary
            sales = reporting.get_sales_summary(db)
            self.assertEqual(sales["total_orders"], 1)
            self.assertEqual(sales["total_units_sold"], 4)
            self.assertEqual(sales["gross_revenue"], 5000.00)

    def test_insufficient_stock_fails_order(self):
        with DatabaseSession(self.db_path) as db:
            user = users.create_user(db, "carol", "carol@nexus.internal")
            prod = products.create_product(db, "SKU-LOW", "Rare Widget", 50.0, "Parts")
            wh = warehouse.create_warehouse(db, "WH-WEST", "Seattle Hub", "Seattle, WA", 1000)
            inventory.set_inventory(db, prod["id"], wh["id"], quantity=2)

            with self.assertRaises(orders.OrderCreationError):
                orders.create_order(db, user["id"], prod["id"], wh["id"], quantity=5)

    def test_migrations(self):
        applied = run_migrations(self.db_path)
        self.assertTrue(len(applied) > 0)


if __name__ == "__main__":
    unittest.main()
