from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import SessionLocal, engine
from .. import models, schemas

from ..core.bot_deps import get_bot_auth
from ..services.igris_core import process_message

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


models.Base.metadata.create_all(bind=engine)


@router.post("/bot/chat")
def bot_chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    _auth: bool = Depends(get_bot_auth)
):

    # Telegram user id comes from bot layer
    user_id = payload.session_id or 0  # or telegram_id mapping

    result = process_message(
        db=db,
        user_id=user_id,
        session_id=payload.session_id,
        message=payload.message,
        role="bot"
    )

    return {
        "response": result["response"],
        "session_id": result["session_id"],
        "source": "telegram"
    }