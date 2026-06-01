from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from .. import models, schemas
from ..core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- REGISTER ----------------
@router.post("/register")
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User exists"
        )

    # 👑 ADMIN AUTO ASSIGN
    role = "admin" if user.email == "michaelkm555@gmail.com" else "user"

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "role": role
    }


# ---------------- LOGIN ----------------
@router.post("/login")
def login(
    user: schemas.UserLogin,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if not db_user or not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # 🔐 JWT WITH ROLE
    token = create_access_token(
        {
            "user_id": db_user.id,
            "role": db_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role
        }
    }