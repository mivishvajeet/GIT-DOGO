"""Nexus Platform REST API Routes and Entrypoint."""

import json
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any
from .config import settings
from .database import DatabaseSession, init_db
from .services import auth, users, products, warehouse, inventory, orders, reporting, events


class NexusApiHandler:
    """Dispatches REST endpoints and returns standard JSON payloads."""

    def __init__(self, db_session: DatabaseSession):
        self.db = db_session

    def handle(self, method: str, path: str, body: Dict[str, Any] = None) -> Dict[str, Any]:
        body = body or {}

        # Healthcheck
        if path == "/health" or path == "/api/v1/health":
            return {"status": "healthy", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}

        # Auth
        if path == "/api/v1/auth/token" and method == "POST":
            token = auth.generate_token(body.get("username", "anonymous"), body.get("role", "user"))
            return {"token": token, "type": "bearer"}

        # Products
        if path == "/api/v1/products":
            if method == "GET":
                return {"products": products.list_products(self.db)}
            elif method == "POST":
                return products.create_product(
                    self.db,
                    sku=body["sku"],
                    name=body["name"],
                    price=float(body["price"]),
                    category=body["category"],
                )

        # Inventory
        if path == "/api/v1/inventory" and method == "POST":
            return inventory.set_inventory(
                self.db,
                product_id=int(body["product_id"]),
                warehouse_id=int(body["warehouse_id"]),
                quantity=int(body["quantity"]),
            )

        # Orders
        if path == "/api/v1/orders" and method == "POST":
            return orders.create_order(
                self.db,
                user_id=int(body["user_id"]),
                product_id=int(body["product_id"]),
                warehouse_id=int(body["warehouse_id"]),
                quantity=int(body["quantity"]),
            )

        # Reporting
        if path == "/api/v1/reporting/inventory" and method == "GET":
            return reporting.get_inventory_summary(self.db)

        if path == "/api/v1/reporting/sales" and method == "GET":
            return reporting.get_sales_summary(self.db)

        # Events
        if path == "/api/v1/events" and method == "GET":
            return {"events": events.list_events(self.db)}

        return {"error": "Not Found", "path": path, "status": 404}


def create_app():
    """Initializes schema and returns ready state."""
    init_db()
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}
