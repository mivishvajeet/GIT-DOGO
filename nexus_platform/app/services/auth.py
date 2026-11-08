"""Authentication and authorization service for Nexus Platform."""

import hashlib
import hmac
import time
from typing import Optional, Dict
from ..config import settings


def generate_token(username: str, role: str = "user") -> str:
    """Generate a signed HMAC token."""
    payload = f"{username}:{role}:{int(time.time())}"
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[Dict[str, str]]:
    """Verify HMAC token signature."""
    parts = token.split(":")
    if len(parts) != 4:
        return None
    username, role, timestamp, signature = parts
    payload = f"{username}:{role}:{timestamp}"
    expected = hmac.new(
        settings.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(expected, signature):
        return {"username": username, "role": role, "timestamp": timestamp}
    return None
