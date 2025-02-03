from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import Column, Integer, text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


Base = declarative_base()


# 모델 정의
class Post(Base):
    __tablename__ = "posts"

    pk = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, server_default=text("'0'"))
    modified_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modified_at = func.now()
