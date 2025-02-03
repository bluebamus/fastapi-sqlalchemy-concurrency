# FastAPI 라우터 생성
from fastapi import APIRouter
from sqlalchemy import text  # ✅ 누락된 import 추가!
from core_app.core.database import engine  # ✅ DB 엔진 가져오기

test_db_router = APIRouter(prefix="/test-db", tags=["Database"])

@test_db_router.get("/")
async def test_db_connection():
    """PostgreSQL 연결 테스트 엔드포인트"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))  # ✅ `text()` 사용!
            db_version = result.scalar()
            return {"status": "✅ Database Connection Successful!", "postgres_version": db_version}
    except Exception as e:
        return {"status": "❌ Database Connection Failed", "error": str(e)}
