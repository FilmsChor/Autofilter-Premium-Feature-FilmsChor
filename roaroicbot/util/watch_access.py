"""Short-lived Prime-only access tokens for browser video playback."""
import hashlib
import hmac
import time
from info import BOT_TOKEN


def create_watch_token(user_id: int, lifetime: int = 21600) -> str:
    expires = int(time.time()) + lifetime
    payload = f"{int(user_id)}.{expires}"
    signature = hmac.new(BOT_TOKEN.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_watch_token(token: str):
    try:
        user_id, expires, signature = token.split(".", 2)
        payload = f"{user_id}.{expires}"
        expected = hmac.new(BOT_TOKEN.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected) or int(expires) < int(time.time()):
            return None
        return int(user_id)
    except (AttributeError, TypeError, ValueError):
        return None
