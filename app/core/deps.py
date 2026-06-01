from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .security import decode_token

# single auth scheme for entire project
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Unified JWT auth dependency for all routes.
    Works for chat, pair, admin, etc.
    """

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("user_id")
    role = payload.get("role", "user")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return {
        "user_id": user_id,
        "role": role
    }