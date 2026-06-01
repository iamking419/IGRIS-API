from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


# ---------------- USERS ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # user | admin | moderator | premium
    role = Column(String, default="user")

    sessions = relationship(
        "ChatSession",
        back_populates="user"
    )

    memories = relationship(
        "Memory",
        back_populates="user"
    )


# ---------------- CHAT SESSIONS (TOPICS) ----------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    title = Column(
        String,
        default="New Chat"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )

    chats = relationship(
        "Chat",
        back_populates="session"
    )

class PairingSession(Base):
    __tablename__ = "pairing_sessions"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    telegram_id = Column(String, index=True)
    user_id = Column(Integer, nullable=True)
    expires_at = Column(DateTime)

# ---------------- CHAT MESSAGES ----------------
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id")
    )

    role = Column(String)  # user | ai

    message = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    session = relationship(
        "ChatSession",
        back_populates="chats"
    )


# ---------------- LONG TERM MEMORY ----------------
class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    key = Column(String)
    value = Column(String)

    # general | user_fact | preference | identity
    type = Column(
        String,
        default="general"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="memories"
    )