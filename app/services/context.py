from .memory import (
    get_recent_chats,
    search_memory
)

from .persona import get_igris_persona


# ---------------- IDENTITY SYSTEM ----------------
def resolve_identity(user_id, role):

    KING_ID = 1  # your real database user id

    if user_id == KING_ID:
        return "king"

    if role == "admin":
        return "admin"

    return "mortal"


# ---------------- CONTEXT ----------------
def build_context(db, user_id, session_id, message, role="user"):

    identity = resolve_identity(user_id, role)

    memory = search_memory(db, user_id, message, limit=8)

    history = get_recent_chats(db, session_id, limit=20)

    # persona now depends on IDENTITY, NOT just role
    persona = get_igris_persona(identity)

    return {
        "user_id": user_id,
        "message": message,
        "memory": memory,
        "history": history,
        "persona": persona,
        "role": role,
        "identity": identity
    }


# ---------------- PROMPT ----------------
def build_prompt(context: dict):

    memory = context.get("memory", [])
    history = context.get("history", [])
    message = context.get("message", "")
    persona = context.get("persona", "")
    identity = context.get("identity", "mortal")

    memory_text = "\n".join(
        [f"- {m.get('key','FACT')}: {m.get('value','')}" for m in memory]
    )

    history_text = "\n".join(
        [f"{c['role'].upper()}: {c['message']}" for c in history]
    )

    return f"""
IDENTITY: {identity}

{persona}

---

MEMORY:
{memory_text if memory_text else "No relevant memory"}

---

HISTORY:
{history_text if history_text else "No history"}

---

CURRENT MESSAGE:
{message}

---

Respond as IGRIS.
"""