from sqlalchemy.orm import Session
from .. import models


# ---------------- USERS ----------------
def get_all_users(db: Session):
    users = db.query(models.User).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]


def get_total_users(db: Session):
    return db.query(models.User).count()


def get_latest_users(db: Session, limit: int = 5):
    users = (
        db.query(models.User)
        .order_by(models.User.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]


# ---------------- CHAT STATS ----------------
def get_total_chats(db: Session):
    return db.query(models.Chat).count()


def get_total_sessions(db: Session):
    return db.query(models.ChatSession).count()


# ---------------- MEMORY STATS ----------------
def get_total_memories(db: Session):
    return db.query(models.Memory).count()