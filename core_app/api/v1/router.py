from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core_app.core.database import get_db
from core_app.models.tables import Post
import threading

core_router = APIRouter(prefix="/test-db", tags=["Database"])


def increase_like(session: Session):
    for _ in range(25):
        post = session.query(Post).filter(Post.pk == 1).first()
        if post:
            print(f"Before increment: like = {post.like}")
            post.like += 1
            print(f"After increment: like = {post.like}")
            session.commit()
            print(f"After commit: like = {post.like}")


# 기본값을 가지는 post의 row를 생성하는 함수
def create_default_post(session: Session):
    # 이미 존재하는지 확인
    post = session.query(Post).filter(Post.pk == 1).first()
    if not post:
        # 기본값으로 새로운 Post 레코드 생성
        new_post = Post(like=0)  # 예시로 pk가 1인 새로운 post 생성
        session.add(new_post)
        session.commit()


@core_router.get("/inc")
def increment_likes(session: Session = Depends(get_db)):
    # post 테이블이 비어있으면 기본값을 가지는 post의 row 생성
    create_default_post(session)

    # like 증가 로직
    increase_like(session)

    post = session.query(Post).filter(Post.pk == 1).first()
    result = post.like if post else 0

    return {"message": "/inc : Concurrent increment completed", "like_result": result}


@core_router.get("/2th")
def concurrent_increment(session: Session = Depends(get_db)):

    create_default_post(session)

    t1 = threading.Thread(target=increase_like, args=(session,))
    t2 = threading.Thread(target=increase_like, args=(session,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    post = session.query(Post).filter(Post.pk == 1).first()
    result = post.like if post else 0

    return {
        "message": "/2th : Concurrent increment completed",
        "like_result": result,
    }


@core_router.get("/init")
def initialize_likes(session: Session = Depends(get_db)):
    post = session.query(Post).filter(Post.pk == 1).first()
    if post:
        post.like = 0
        session.commit()
        return {
            "message": "/init : Like count initialized to 0",
            "like_result": post.like,
        }
    return {"message": "Post not found", "like_result": None}


@core_router.get("/like")
def get_like_count(session: Session = Depends(get_db)):
    post = session.query(Post).filter(Post.pk == 1).first()
    if post:
        return {
            "message": "/like : Current like count",
            "like_result": post.like,
            "modified_at": post.modified_at,
        }
    return {"message": "Post not found", "like_result": None}
