from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=5,  # 커넥션 풀 크기
    max_overflow=10,  # 최대 초과 커넥션
    echo=settings.SQL_DEBUG,  # SQL 로깅
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 데이터베이스 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
