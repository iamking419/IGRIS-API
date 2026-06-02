from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.security import get_current_user

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
def create_session(
    payload: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    session = models.ChatSession(
        user_id=current_user.id,
        title=payload.title
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# ---------------- GET ALL SESSIONS ----------------
@router.get("/sessions", response_model=list[schemas.ChatSessionOut])
def get_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.id.desc()).all()

    return sessions


# ---------------- UPDATE SESSION TITLE ----------------
@router.get("/sessions", response_model=list[schemas.ChatSessionOut])
def get_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.id.desc()).all()

    return session
# ---------------- RENAME SESSION TITLE ----------------
@router.patch("/sessions/{session_id}")
def rename_session(
    session_id: int,
    payload: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = payload.title
    db.commit()

    return {"message": "renamed"}

# ---------------- DELETE SESSION ----------------
@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()

    return {"message": "deleted"}
