from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import Column, Integer, text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import INTEGER


Base = declarative_base()


def custom_version_generator(current_version):
    return current_version + 1  # 현재 버전에서 1을 증가시킴


# 모델 정의
class Post(Base):
    __tablename__ = "posts"

    pk = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, server_default=text("'0'"))
    version = Column(INTEGER(unsigned=True), server_default=text("'0'"), nullable=False)
    modified_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # __mapper_args__ = {"version_id_col": version}

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": custom_version_generator,  # 커스텀 버전 증가 함수 설정
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modified_at = func.now()
