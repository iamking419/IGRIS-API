from fastapi import APIRouter
from ..db import engine
from sqlalchemy import text

router = APIRouter()

@router.get("/db-test")
def db_test():
    try:
        conn = engine.connect()
        result = conn.execute(text("SELECT 1"))
        conn.close()

        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }