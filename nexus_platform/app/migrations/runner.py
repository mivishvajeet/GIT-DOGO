"""Database migration runner (Alembic-compatible execution)."""

from pathlib import Path
from typing import List
from ..database import DatabaseSession, DB_FILE


class MigrationError(Exception):
    pass


MIGRATIONS = [
    (
        "001_initial_schema",
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ),
    (
        "002_add_warehouse_zones",
        """
        ALTER TABLE warehouses ADD COLUMN zone_code TEXT DEFAULT 'DEFAULT_ZONE';
        """
    ),
    (
        "003_add_order_notes",
        """
        ALTER TABLE orders ADD COLUMN notes TEXT DEFAULT '';
        """
    )
]


def run_migrations(db_path: Path = DB_FILE) -> List[str]:
    """Applies pending migrations in sequence."""
    applied = []
    with DatabaseSession(db_path) as db:
        # Ensure tracking table exists
        db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur = db.execute("SELECT version FROM schema_migrations")
        existing = {r["version"] for r in cur.fetchall()}

        for version, sql in MIGRATIONS:
            if version not in existing:
                try:
                    for statement in sql.strip().split(";"):
                        if statement.strip():
                            db.execute(statement)
                    db.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                    applied.append(version)
                except Exception as e:
                    raise MigrationError(f"Migration {version} failed: {e}") from e

    return applied
