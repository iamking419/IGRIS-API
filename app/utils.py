from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from .core.config import SECRET_KEY 


ALGORITHM = "HS256"

# bcrypt has a 72-byte limit for password input. bcrypt_sha256 hashes the password
# with SHA-256 first, avoiding truncation issues for long passwords.
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_minutes=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)