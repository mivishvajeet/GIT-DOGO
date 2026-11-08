"""Event processing and audit stream."""

import json
from typing import Dict, Any, List
from ..database import DatabaseSession


def record_event(db: DatabaseSession, event_type: str, payload: Dict[str, Any]) -> int:
    db.execute(
        "INSERT INTO events (event_type, payload) VALUES (?, ?)",
        (event_type, json.dumps(payload)),
    )
    return db.cursor.lastrowid


def list_events(db: DatabaseSession, event_type: str = None) -> List[Dict[str, Any]]:
    if event_type:
        cur = db.execute("SELECT * FROM events WHERE event_type = ? ORDER BY id DESC", (event_type,))
    else:
        cur = db.execute("SELECT * FROM events ORDER BY id DESC")
    results = []
    for row in cur.fetchall():
        d = dict(row)
        d["payload"] = json.loads(d["payload"])
        results.append(d)
    return results
