"""User management service."""

from typing import Optional, Dict, Any
from ..database import DatabaseSession


def create_user(db: DatabaseSession, username: str, email: str, role: str = "user") -> Dict[str, Any]:
    db.execute(
        "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
        (username, email, role)
    )
    user_id = db.cursor.lastrowid
    return {"id": user_id, "username": username, "email": email, "role": role}


def get_user_by_id(db: DatabaseSession, user_id: int) -> Optional[Dict[str, Any]]:
    cur = db.execute("SELECT id, username, email, role, created_at FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        return dict(row)
    return None

