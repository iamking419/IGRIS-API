from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, utils

# Google OAuth imports
from google.oauth2 import id_token
from google.auth.transport import requests
import os

# Google Client ID (set this in Render / .env)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# =========================
# CREATE USER (EMAIL/PASS)
# =========================
def create_user(db: Session, user):
    hashed = utils.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# =========================
# LOGIN USER (EMAIL/PASS)
# =========================
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        return None

    if not utils.verify_password(password, user.hashed_password):
        return None

    return user


# =========================
# GOOGLE OAUTH LOGIN
# =========================
def authenticate_google_user(db: Session, token: str):
    try:
        # Verify token with Google
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = payload.get("email")
        username = payload.get("name") or email.split("@")[0]
        google_id = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Google account has no email"
            )

        # Check if user exists
        user = db.query(models.User).filter(
            models.User.email == email
        ).first()

        # Create user if not exists
        if not user:
            user = models.User(
                username=username,
                email=email,
                hashed_password=None  # Google users have no password
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Google authentication failed: {str(e)}"
        )