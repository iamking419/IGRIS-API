import os

# SECURITY KEYS
SECRET_KEY = os.getenv("SECRET_KEY", "igris_secret_key_change_me")

# AI CONFIG
AI_API_URL = os.getenv(
    "AI_API_URL",
    "https://heavstal.com.ng/api/v1/jeden"
)

AI_API_KEY = os.getenv(
    "AI_API_KEY",
    "ht_live_6cbb8dda46ca1dc0ed10d95953a9a6575df61f0781dda42a"
)

# BOT SECURITY KEY (Telegram / system trust layer)
BOT_SECRET_TOKEN = os.getenv(
    "BOT_SECRET_TOKEN",
    "igris_bot_9f83k2kls9x_ishim"
)

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "736442979434-025v4c5m7nkch91rok9jprsuegk9i48m.apps.googleusercontent.com"
    )
