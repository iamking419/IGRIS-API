from fastapi import Header, HTTPException
from ..core.config import BOT_SECRET_TOKEN


def get_bot_auth(authorization: str = Header(None)):
    """
    Simple shared-secret auth for Telegram bot → API
    """

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing bot auth")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid bot auth format")

    token = parts[1]

    if token != BOT_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bot token")

    return True