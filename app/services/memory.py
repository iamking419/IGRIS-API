from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from .. import models


# ---------------- CHAT ----------------

def save_chat(db: Session, session_id: int, role: str, message: str):

    chat = models.Chat(
        session_id=session_id,
        role=role,
        message=message,
        created_at=datetime.utcnow()
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_recent_chats(db: Session, session_id: int, limit: int = 20):

    chats = (
        db.query(models.Chat)
        .filter(models.Chat.session_id == session_id)
        .order_by(models.Chat.id.desc())
        .limit(limit)
        .all()
    )

    chats.reverse()

    return [
        {"role": c.role, "message": c.message}
        for c in chats
    ]


# ---------------- MEMORY ----------------

def set_memory(
    db: Session,
    user_id: int,
    key: str,
    value: str,
    mtype: str = "general"
):

    """
    Stores memory WITHOUT overwriting unless same key exists.
    Adds memory type for smarter AI usage.
    """

    memory = models.Memory(
        user_id=user_id,
        key=key,
        value=value,
        type=mtype,
        created_at=datetime.utcnow()
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def get_memory(db: Session, user_id: int):

    memories = (
        db.query(models.Memory)
        .filter(models.Memory.user_id == user_id)
        .all()
    )

    return [
        {
            "key": m.key,
            "value": m.value,
            "type": getattr(m, "type", "general")
        }
        for m in memories
    ]


def search_memory(db: Session, user_id: int, query: str, limit: int = 5):

    """
    SIMPLE semantic-ish search (upgrade later to embeddings)
    """

    query = query.lower()

    memories = (
        db.query(models.Memory)
        .filter(models.Memory.user_id == user_id)
        .all()
    )

    scored = []

    for m in memories:
        text = (m.value or "").lower()

        score = 0

        # simple relevance scoring
        if query in text:
            score += 5

        common_words = set(query.split()) & set(text.split())
        score += len(common_words)

        if score > 0:
            scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "key": m.key,
            "value": m.value,
            "type": getattr(m, "type", "general")
        }
        for score, m in scored[:limit]
    ]


def set_or_update_memory(
    db: Session,
    user_id: int,
    key: str,
    value: str,
    mtype: str = "general"
):

    """
    Safer update version (optional use)
    """

    memory = (
        db.query(models.Memory)
        .filter(
            models.Memory.user_id == user_id,
            models.Memory.key == key
        )
        .first()
    )

    if memory:
        memory.value = value
        memory.type = mtype
    else:
        memory = models.Memory(
            user_id=user_id,
            key=key,
            value=value,
            type=mtype,
            created_at=datetime.utcnow()
        )
        db.add(memory)

    db.commit()
    return memory