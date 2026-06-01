import requests
import telebot
import os

from app.db import SessionLocal
from app.services.pairing import create_pair_session

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "8254458626:AAHwhFEuRKs9OS2YLgCsWFneUsaI8UThMfw")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/bot/chat")

BOT_SECRET = os.getenv("BOT_SECRET", "igris_bot_9f83k2kls9x_ishim")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        """
⚔️ IGRIS ONLINE

System Status: ACTIVE

━━━━━━━━━━━━━━━
You can:
• Chat with IGRIS directly here
• Link your Web account for shared memory

🔗 LINK SYSTEM:
/link → generate pairing code

After linking:
✔ Same memory (Web + Telegram)
✔ Same identity
✔ Continuous conversation history

NOTE BOT IS STILL IN DEVELOPMENT

State your command, mortal.
"""
    )


# ---------------- LINK SYSTEM ----------------
@bot.message_handler(commands=['link'])
def link(message):

    db = get_db()
    telegram_id = str(message.chat.id)

    code = create_pair_session(db, telegram_id)

    bot.reply_to(
        message,
        f"""
🔗 IGRIS PAIRING CODE

{code}

━━━━━━━━━━━━━━━
Enter this code in your web dashboard.

⏳ Expires in 10 minutes

Result after linking:
✔ Unified identity
✔ Shared memory across platforms
"""
    )


# ---------------- CHAT HANDLER ----------------
@bot.message_handler(func=lambda m: True)
def handle_message(message):

    telegram_id = str(message.chat.id)
    text = message.text or ""

    payload = {
        "message": text,
        "session_id": None,
        "telegram_id": telegram_id
    }

    headers = {
        "Authorization": f"Bearer {BOT_SECRET}"
    }

    try:
        res = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        if res.status_code != 200:
            bot.reply_to(message, "⚠️ IGRIS backend error.")
            return

        data = res.json()

        bot.reply_to(
            message,
            data.get("response", "No response from IGRIS")
        )

    except Exception as e:
        bot.reply_to(
            message,
            f"⚠️ IGRIS ERROR:\n{str(e)}"
        )


print("⚔️ IGRIS BOT RUNNING...")

bot.infinity_polling(skip_pending=True)