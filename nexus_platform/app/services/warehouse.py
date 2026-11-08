"""Warehouse management service."""

from typing import Optional, Dict, Any, List
from ..database import DatabaseSession


def create_warehouse(
    db: DatabaseSession, code: str, name: str, location: str, capacity: int
) -> Dict[str, Any]:
    db.execute(
        "INSERT INTO warehouses (code, name, location, capacity) VALUES (?, ?, ?, ?)",
        (code, name, location, capacity),
    )
    warehouse_id = db.cursor.lastrowid
    return {"id": warehouse_id, "code": code, "name": name, "location": location, "capacity": capacity}


def get_warehouse(db: DatabaseSession, warehouse_id: int) -> Optional[Dict[str, Any]]:
    cur = db.execute("SELECT * FROM warehouses WHERE id = ?", (warehouse_id,))
    row = cur.fetchone()
    return dict(row) if row else None

