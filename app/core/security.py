from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from .config import SECRET_KEY

# ---------------- CONFIG ----------------

ALGORITHM = "HS256"

# ---------------- PASSWORD HANDLER ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- JWT SYSTEM ----------------
def create_access_token(data: dict, expires_minutes: int = 2880) -> str:
    """
    Create JWT access token with expiration.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Decode JWT token and return payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ---------------- OPTIONAL (FUTURE USE) ----------------
def get_user_id_from_token(token: str):
    """
    Safe helper to extract user_id directly.
    """
    payload = decode_token(token)
    if not payload:
        return None

    return payload.get("user_id")
