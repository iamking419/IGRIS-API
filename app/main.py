from fastapi import FastAPI
from fastapi.security import HTTPBearer
from .routes import auth, chat, health , sessions,pair
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="IGRIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Or specify your Development App URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(pair.router)
app.include_router(sessions.router)

app.include_router(auth.router, prefix="/auth")




@app.get("/")
def home():
    return {"message": "IGRIS API is alive"}
