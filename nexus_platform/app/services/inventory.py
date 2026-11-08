"""Inventory management service: stock allocation, reservation and auditing."""

from typing import Optional, Dict, Any, List
from ..database import DatabaseSession


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available unreserved stock."""
    pass


def set_inventory(
    db: DatabaseSession, product_id: int, warehouse_id: int, quantity: int
) -> Dict[str, Any]:
    cur = db.execute(
        "SELECT id, quantity, reserved_quantity FROM inventory_items WHERE product_id = ? AND warehouse_id = ?",
        (product_id, warehouse_id),
    )
    row = cur.fetchone()
    if row:
        db.execute(
            "UPDATE inventory_items SET quantity = ? WHERE id = ?",
            (quantity, row["id"]),
        )
        item_id = row["id"]
    else:
        db.execute(
            "INSERT INTO inventory_items (product_id, warehouse_id, quantity, reserved_quantity) VALUES (?, ?, ?, 0)",
            (product_id, warehouse_id, quantity),
        )
        item_id = db.cursor.lastrowid

    return {
        "id": item_id,
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "quantity": quantity,
    }


def reserve_stock(
    db: DatabaseSession, product_id: int, warehouse_id: int, qty: int
) -> None:
    cur = db.execute(
        "SELECT id, quantity, reserved_quantity FROM inventory_items WHERE product_id = ? AND warehouse_id = ?",
        (product_id, warehouse_id),
    )
    row = cur.fetchone()
    if not row:
        raise InsufficientStockError(f"No inventory record for product {product_id} in warehouse {warehouse_id}")

    available = row["quantity"] - row["reserved_quantity"]
    if available < qty:
        raise InsufficientStockError(
            f"Insufficient stock: requested {qty}, available {available} (total {row['quantity']})"
        )

    db.execute(
        "UPDATE inventory_items SET reserved_quantity = reserved_quantity + ? WHERE id = ?",
        (qty, row["id"]),
    )


def release_stock(
    db: DatabaseSession, product_id: int, warehouse_id: int, qty: int
) -> None:
    db.execute(
        "UPDATE inventory_items SET reserved_quantity = MAX(0, reserved_quantity - ?) WHERE product_id = ? AND warehouse_id = ?",
        (qty, product_id, warehouse_id),
    )


def get_stock_level(
    db: DatabaseSession, product_id: int, warehouse_id: int
) -> Dict[str, int]:
    cur = db.execute(
        "SELECT quantity, reserved_quantity FROM inventory_items WHERE product_id = ? AND warehouse_id = ?",
        (product_id, warehouse_id),
    )
    row = cur.fetchone()
    if not row:
        return {"quantity": 0, "reserved": 0, "available": 0}
    return {
        "quantity": row["quantity"],
        "reserved": row["reserved_quantity"],
        "available": row["quantity"] - row["reserved_quantity"],
    }

