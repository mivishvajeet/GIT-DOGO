"""Order management service: coordinates users, products, warehouses, and inventory."""

from typing import Dict, Any, Optional
from ..database import DatabaseSession
from .users import get_user_by_id
from .products import get_product
from .warehouse import get_warehouse
from .inventory import reserve_stock, InsufficientStockError
from .events import record_event


class OrderCreationError(Exception):
    """Raised when order creation fails business rules."""
    pass


def create_order(
    db: DatabaseSession,
    user_id: int,
    product_id: int,
    warehouse_id: int,
    quantity: int,
) -> Dict[str, Any]:
    """Execute end-to-end transactional order creation."""
    # 1. Validate user
    user = get_user_by_id(db, user_id)
    if not user:
        raise OrderCreationError(f"User {user_id} does not exist")

    # 2. Validate product
    product = get_product(db, product_id)
    if not product or not product.get("is_active"):
        raise OrderCreationError(f"Product {product_id} is inactive or non-existent")

    # 3. Validate warehouse
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        raise OrderCreationError(f"Warehouse {warehouse_id} does not exist")

    # 4. Reserve inventory
    try:
        reserve_stock(db, product_id, warehouse_id, quantity)
    except InsufficientStockError as e:
        raise OrderCreationError(str(e)) from e

    # 5. Calculate total
    total_amount = round(product["price"] * quantity, 2)

    # 6. Insert Order
    db.execute(
        """
        INSERT INTO orders (user_id, product_id, warehouse_id, quantity, status, total_amount)
        VALUES (?, ?, ?, ?, 'confirmed', ?)
        """,
        (user_id, product_id, warehouse_id, quantity, total_amount),
    )
    order_id = db.cursor.lastrowid

    # 7. Record Domain Event
    record_event(
        db,
        "ORDER_PLACED",
        {
            "order_id": order_id,
            "user_id": user_id,
            "product_id": product_id,
            "total_amount": total_amount,
        },
    )

    return {
        "order_id": order_id,
        "user_id": user_id,
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "quantity": quantity,
        "status": "confirmed",
        "total_amount": total_amount,
    }
