from .context import build_context, build_prompt
from .ai_engine import generate_response
from .memory import save_chat, set_memory


def process_message(db, user_id, session_id, message, role="user"):
    msg = message.strip()

    # ---------------- MEMORY TRIGGER ----------------
    if msg.lower().startswith("remember"):
        fact = msg[8:].strip()

        if fact:
            set_memory(
                db=db,
                user_id=user_id,
                key=f"memory_{user_id}_{hash(fact)}",
                value=fact
            )

    # ---------------- CONTEXT (YOUR EXISTING SYSTEM) ----------------
    context = build_context(
        db=db,
        user_id=user_id,
        session_id=session_id,
        message=msg,
        role=role
    )

    prompt = build_prompt(context)

    # ---------------- AI ----------------
    response = generate_response(prompt)

    # ---------------- SAVE GLOBAL MEMORY ----------------
    save_chat(db, session_id, "user", msg)
    save_chat(db, session_id, "ai", response)

    return {
        "response": response,
        "session_id": session_id,
        "role": role
    }