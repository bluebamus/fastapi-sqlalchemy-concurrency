from fastapi import FastAPI
from core_app.core.config import settings
from core_app.test.db_con_test import test_db_router
from core_app.api.v1.router import core_router


# 설정값 출력 (테스트)
# [print(f"{key}: {value}") for key, value in settings.model_dump().items()]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Test project to solve concurrency problem based on fastapi and sqlalchemy",
)

# 라우터 추가
app.include_router(test_db_router)
app.include_router(core_router)

# 데이터베이스 테이블 생성
# result = Base.metadata.create_all(bind=engine)
