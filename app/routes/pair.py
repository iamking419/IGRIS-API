from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..services.pairing import link_account
from ..core.deps import get_current_user
from ..schemas import PairRequest

router = APIRouter()


# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- LINK ACCOUNT ----------------
@router.post("/link-account")
def link_web_account(
    payload: PairRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["user_id"]

    # validate code
    code = payload.code

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Pairing code is required"
        )

    telegram_id = link_account(
        db=db,
        code=code,
        user_id=user_id
    )

    if not telegram_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired pairing code"
        )

    return {
        "message": "Accounts linked successfully ⚔️",
        "telegram_id": telegram_id,
        "user_id": user_id
    }