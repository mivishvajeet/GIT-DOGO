"""Reporting service: business metrics, inventory valuation, and sales aggregations."""

from typing import Dict, Any, List
from ..database import DatabaseSession


def get_inventory_summary(db: DatabaseSession) -> Dict[str, Any]:
    """Calculate aggregated stock and total inventory value."""
    cur = db.execute("""
        SELECT 
            COUNT(DISTINCT p.id) as total_products,
            COALESCE(SUM(i.quantity), 0) as total_units_in_stock,
            COALESCE(SUM(i.reserved_quantity), 0) as total_units_reserved,
            COALESCE(SUM(i.quantity * p.price), 0.0) as total_inventory_valuation
        FROM products p
        LEFT JOIN inventory_items i ON p.id = i.product_id
    """)
    row = cur.fetchone()
    return dict(row) if row else {}


def get_sales_summary(db: DatabaseSession) -> Dict[str, Any]:
    """Calculate total orders and gross revenue."""
    cur = db.execute("""
        SELECT
            COUNT(id) as total_orders,
            COALESCE(SUM(quantity), 0) as total_units_sold,
            COALESCE(SUM(total_amount), 0.0) as gross_revenue
        FROM orders
        WHERE status = 'confirmed'
    """)
    row = cur.fetchone()
    return dict(row) if row else {}
