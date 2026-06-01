from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from .. import models, schemas

router = APIRouter()


# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- CREATE SESSION ----------------
@router.post("/sessions", response_model=schemas.ChatSessionOut)
def create_session(payload: schemas.ChatSessionCreate, db: Session = Depends(get_db)):

    user_id = 1  # TEMP (JWT later)

    session = models.ChatSession(
        user_id=user_id,
        title=payload.title
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# ---------------- GET ALL SESSIONS ----------------
@router.get("/sessions", response_model=list[schemas.ChatSessionOut])
def get_sessions(db: Session = Depends(get_db)):

    user_id = 1  # TEMP

    sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user_id
    ).order_by(models.ChatSession.id.desc()).all()

    return sessions


# ---------------- UPDATE SESSION TITLE ----------------
@router.patch("/sessions/{session_id}")
def rename_session(session_id: int, payload: schemas.ChatSessionCreate, db: Session = Depends(get_db)):

    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = payload.title
    db.commit()

    return {"message": "renamed"}


# ---------------- DELETE SESSION ----------------
@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):

    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()

    return {"message": "deleted"}