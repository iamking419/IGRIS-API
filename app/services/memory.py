from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import re
import hashlib
import math

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
    return [{"role": c.role, "message": c.message} for c in chats]


# ---------------- MEMORY ----------------

def set_memory(
    db: Session,
    user_id: int,
    key: str,
    value: str,
    mtype: str = "general"
):
    """
    Stores memory. If same key exists for this user, returns existing
    (no overwrite). Use set_or_update_memory() to overwrite.
    """
    existing = (
        db.query(models.Memory)
        .filter(models.Memory.user_id == user_id, models.Memory.key == key)
        .first()
    )
    if existing:
        return existing

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
    SIMPLE semantic-ish search (legacy keyword fallback).
    Prefer search_memory_smart() for production use.
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
    Safer update version. Creates or overwrites existing key.
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
    db.refresh(memory)
    return memory


# ---------------- INNOVATIONS ----------------

def _deterministic_key(mtype: str, text: str) -> str:
    """Creates a content-based key so exact duplicates are impossible."""
    short = re.sub(r'\W+', ' ', text[:60]).lower().strip()
    digest = hashlib.md5(short.encode()).hexdigest()[:8]
    return f"{mtype}:{digest}"


def extract_chat_memories(db: Session, session_id: int, user_id: int, scan_limit: int = 10):
    """
    Auto-extracts facts from recent user messages and stores them as typed memories.
    Call this after each user turn (or use remember_chat_turn()).
    """
    chats = get_recent_chats(db, session_id, limit=scan_limit)
    patterns = {
        "preference": r"(?i)\b(i like|i love|i hate|i dislike|i prefer|my favorite)\b",
        "identity":   r"(?i)\b(i am|i'm|my name is|i work as|i live in|i study at)\b",
        "goal":       r"(?i)\b(i want to|i need to|i plan to|my goal is|i'm trying to)\b",
        "constraint": r"(?i)\b(i can't|i cannot|i'm allergic to|i don't have|i never)\b",
    }
    extracted = 0
    for msg in chats:
        if msg["role"] != "user":
            continue
        text = msg["message"]
        for mtype, pattern in patterns.items():
            if re.search(pattern, text):
                key = _deterministic_key(mtype, text)
                set_or_update_memory(db, user_id, key, text, mtype=mtype)
                extracted += 1
    return extracted


def remember_chat_turn(db: Session, session_id: int, user_id: int, role: str, message: str):
    """
    Memory-aware chat logging. Saves the message, then auto-extracts
    facts if it's from the user.
    """
    chat = save_chat(db, session_id, role, message)
    if role == "user":
        extract_chat_memories(db, session_id, user_id, scan_limit=3)
    return chat


def search_memory_smart(db: Session, user_id: int, query: str, limit: int = 5):
    """
    Recency-weighted semantic search. Older memories decay unless highly relevant.
    """
    query = query.lower()
    q_words = set(query.split())
    now = datetime.utcnow()
    memories = db.query(models.Memory).filter(models.Memory.user_id == user_id).all()
    scored = []
    for m in memories:
        text = (m.value or "").lower()
        key = (m.key or "").lower()
        relevance = 0
        if query in text:
            relevance += 10
        if query in key:
            relevance += 8
        text_words = set(text.split())
        key_words = set(key.split())
        relevance += len(q_words & text_words) * 2
        relevance += len(q_words & key_words) * 3
        if relevance == 0:
            continue
        created = getattr(m, "created_at", now)
        age_days = max(0, (now - created).days)
        recency = math.exp(-age_days / 30.0)
        score = relevance * (1 + recency)
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "key": m.key,
            "value": m.value,
            "type": getattr(m, "type", "general"),
            "score": round(score, 3)
        }
        for score, m in scored[:limit]
    ]


def build_ai_context(
    db: Session,
    session_id: int,
    user_id: int,
    current_message: str = "",
    chat_window: int = 8
):
    """
    One-shot context assembler. Returns everything the LLM needs:
    recent chat, relevant memories, and a ready-to-inject prompt string.
    """
    recent_chat = get_recent_chats(db, session_id, limit=chat_window)
    relevant_memories = (
        search_memory_smart(db, user_id, current_message, limit=5)
        if current_message else []
    )
    memory_prompt = ""
    if relevant_memories:
        lines = ["## Facts you remember about this user:"]
        for m in relevant_memories:
            tag = m.get("type", "general").upper()
            lines.append(f"- [{tag}] {m['value']}")
        memory_prompt = "\n".join(lines)
    return {
        "recent_chat": recent_chat,
        "relevant_memories": relevant_memories,
        "memory_prompt": memory_prompt,
        "session_id": session_id,
        "user_id": user_id,
    }


def consolidate_memories(db: Session, user_id: int):
    """
    Fixes legacy duplicate keys by keeping only the NEWEST record per key.
    Returns number of duplicates purged.
    """
    memories = (
        db.query(models.Memory)
        .filter(models.Memory.user_id == user_id)
        .order_by(models.Memory.id.desc())
        .all()
    )
    seen = set()
    purged = 0
    for m in memories:
        if m.key in seen:
            db.delete(m)
            purged += 1
        else:
            seen.add(m.key)
    db.commit()
    return purged


def format_memories_for_prompt(db: Session, user_id: int, query: str = "") -> str:
    """
    Returns a pre-formatted memory block for system prompt injection.
    """
    mems = (
        search_memory_smart(db, user_id, query, limit=6)
        if query else get_memory(db, user_id)[:6]
    )
    if not mems:
        return ""
    lines = ["## User Profile (recall these facts):"]
    for m in mems:
        tag = m.get("type", "general").upper()
        lines.append(f"- [{tag}] {m['value']}")
    return "\n".join(lines)
