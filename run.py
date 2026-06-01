import subprocess
import sys
import time


print("⚔️ Starting IGRIS System...")


# ---------------- START FASTAPI ----------------
api = subprocess.Popen([
    sys.executable, "-m",
    "uvicorn", "app.main:app",
    "--reload"
])


# allow backend to boot first
time.sleep(3)


# ---------------- START BOT ----------------
bot = subprocess.Popen([
    sys.executable,
    "bot.py"
])


print("✔ IGRIS ONLINE (API + BOT RUNNING)")


# keep alive
api.wait()
bot.wait()