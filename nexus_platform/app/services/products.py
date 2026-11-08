"""Product catalogue service."""

from typing import Optional, Dict, Any, List
from ..database import DatabaseSession


def create_product(
    db: DatabaseSession, sku: str, name: str, price: float, category: str
) -> Dict[str, Any]:
    db.execute(
        "INSERT INTO products (sku, name, price, category) VALUES (?, ?, ?, ?)",
        (sku, name, price, category),
    )
    product_id = db.cursor.lastrowid
    return {"id": product_id, "sku": sku, "name": name, "price": price, "category": category}


def get_product(db: DatabaseSession, product_id: int) -> Optional[Dict[str, Any]]:
    cur = db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def list_products(db: DatabaseSession) -> List[Dict[str, Any]]:
    cur = db.execute("SELECT * FROM products WHERE is_active = 1")
    return [dict(r) for r in cur.fetchall()]
