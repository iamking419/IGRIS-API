from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import SessionLocal, engine
from .. import models, schemas

from ..core.deps import get_current_user
from ..services.igris_core import process_message

from ..services.admin import (
    get_all_users,
    get_total_users,
    get_latest_users,
    get_total_chats,
    get_total_memories
)

router = APIRouter()


# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- INIT DB TABLES ----------------
#models.Base.metadata.create_all(bind=engine)


# ---------------- CHAT ENDPOINT ----------------
@router.post("/chat")
def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["user_id"]
    role = current_user["role"]

    message = payload.message.strip()
    session_id = payload.session_id


    # ---------------- SESSION CREATION ----------------
    if not session_id:
        session = models.ChatSession(
            user_id=user_id,
            title=message[:40] or "New Chat"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id


    # ---------------- SESSION VALIDATION ----------------
    else:
        session = (
            db.query(models.ChatSession)
            .filter(models.ChatSession.id == session_id)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        if session.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized session access"
            )


    # ---------------- ADMIN COMMAND LAYER ----------------
    if role == "admin":
        cmd = message.lower().strip()

        if cmd == "show all users":
            return {"admin": True, "users": get_all_users(db)}

        if cmd == "total users":
            return {"admin": True, "total_users": get_total_users(db)}

        if cmd == "latest users":
            return {"admin": True, "latest_users": get_latest_users(db)}

        if cmd == "total chats":
            return {"admin": True, "total_chats": get_total_chats(db)}

        if cmd == "total memories":
            return {"admin": True, "total_memories": get_total_memories(db)}


    # ---------------- ⚔️ UNIFIED IGRIS CORE ----------------
    result = process_message(
        db=db,
        user_id=user_id,
        session_id=session_id,
        message=message,
        role=role
    )

    # ---------------- RESPONSE ----------------
    return {
        "response": result["response"],
        "session_id": result["session_id"],
        "role": role,
        "user_id": user_id
    }
