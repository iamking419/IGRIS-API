import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .. import models


# ---------------- GENERATE CODE ----------------
def generate_pair_code():
    return str(random.randint(10000, 99999))


# ---------------- CREATE PAIR SESSION ----------------
def create_pair_session(db: Session, telegram_id: str):
    code = generate_pair_code()

    session = models.PairingSession(
        code=code,
        telegram_id=telegram_id,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        user_id=None
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return code


# ---------------- LINK ACCOUNTS ----------------
def link_account(db: Session, code: str, user_id: int):

    session = (
        db.query(models.PairingSession)
        .filter(models.PairingSession.code == code)
        .first()
    )

    if not session:
        return None

    if session.expires_at < datetime.utcnow():
        return None

    # already linked protection
    if session.user_id:
        return session.telegram_id

    session.user_id = user_id
    db.commit()

    return session.telegram_id


# ---------------- GET USER FROM TELEGRAM ----------------
def get_user_by_telegram(db: Session, telegram_id: str):
    """
    Used by webhook to map Telegram → Web user
    """
    return (
        db.query(models.PairingSession)
        .filter(
            models.PairingSession.telegram_id == telegram_id,
            models.PairingSession.user_id.isnot(None),
            models.PairingSession.expires_at > datetime.utcnow()
        )
        .first()
    )