from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core_app.core.database import get_db
from core_app.models.tables import Post
import threading

from sqlalchemy.orm.attributes import set_committed_value

from core_app.core.config import setup_logger

core_router = APIRouter(prefix="/test-db", tags=["Database"])


def increase_like(session: Session):
    for _ in range(25):
        post = session.query(Post).filter(Post.pk == 1).first()
        if post:
            print(f"Before increment: like = {post.like}")
            post.like += 1
            session.commit()
            print(f"After commit: like = {post.like}")
            session.close()


def increase_like_with_pessimistic_lock(session: Session):
    thread_id = threading.get_ident()  # 현재 스레드 ID
    logger = setup_logger(thread_id)  # 스레드별 로거 설정
    session_id = id(session)
    cnt = 0
    for _ in range(25):
        try:
            cnt = cnt + 1
            post = session.query(Post).filter(Post.pk == 1).with_for_update().first()

            if post:
                logger.info(
                    f"Thread {thread_id} (Session ID: {session_id}) acquired lock. Before ---- increment: like = {post.like}"
                )
                post.like += 1
                session.commit()
                logger.info(
                    f"Thread {thread_id} (Session ID: {session_id}) released lock. After **** commit: like = {post.like}"
                )
                session.close()

        except Exception as e:
            logger.info(f"Thread {thread_id} encountered an error: {e}")
            session.rollback()
    logger.info(
        f"Thread {thread_id} (Session ID: {session_id}) end of thread cnt = {cnt}"
    )


def increase_like_by_optimistic_lock(session: Session):
    thread_id = threading.get_ident()  # 현재 스레드 ID
    logger = setup_logger(thread_id)  # 스레드별 로거 설정
    session_id = id(session)
    cnt = 0
    range_cnt = 25
    while cnt < range_cnt:
        cnt = cnt + 1
        post = session.query(Post).filter(Post.pk == 1).first()
        logger.info(
            f"Thread {thread_id} (Session ID: {session_id}) acquired lock. Before ---- increment: like = {post.like}"
        )
        result = (
            session.query(Post)
            .filter(Post.pk == post.pk, Post.version == post.version)
            .update({Post.like: post.like + 1, Post.version: post.version + 1})
        )

        if result == 0:
            logger.error(
                f"Thread {thread_id} (Session ID: {session_id}) failed to update: version mismatch."
            )
            session.rollback()  # 롤백
            cnt -= 1
            continue

        updated_post = session.query(Post).filter(Post.pk == post.pk).first()

        if not bool(result):
            session.rollback()
        else:
            session.commit()
            logger.info(
                f"Thread {thread_id} (Session ID: {session_id}) released lock. After **** commit: like = {updated_post.like}"
            )
            logger.info(
                f"Thread {thread_id} (Session ID: {session_id}) end of thread cnt = {cnt}"
            )
            session.close()


def increase_like_by_optimistic_lock_sqlalchemy_versioning(session: Session):
    thread_id = threading.get_ident()  # 현재 스레드 ID
    logger = setup_logger(thread_id)  # 스레드별 로거 설정
    session_id = id(session)
    cnt = 0
    range_cnt = 25
    while cnt < range_cnt:
        cnt += 1
        try:
            post = session.query(Post).filter(Post.pk == 1).first()
            logger.info(
                f"Thread {thread_id} (Session ID: {session_id}) acquired lock. Before ---- increment: like = {post.like}, version = {post.version}"
            )
            # 버전 증가 및 좋아요 수 증가
            post.like += 1

            # 업데이트 쿼리 실행
            result = (
                session.query(Post)
                .filter(
                    Post.pk == post.pk, Post.version == post.version
                )  # 이전 버전으로 필터링
                .update({Post.like: post.like, Post.version: post.version + 1})
            )

            if result == 0:
                logger.error(
                    f"Thread {thread_id} (Session ID: {session_id}) failed to update: version mismatch."
                )
                session.rollback()  # 롤백
                cnt -= 1
                continue  # 다음 반복으로 넘어감

            session.commit()  # 성공적으로 업데이트된 경우 커밋
            session.refresh(post)  # 최신 상태로 새로 고침
            logger.info(
                f"Thread {thread_id} (Session ID: {session_id}) released lock. After **** commit: like = {post.like}, version = {post.version}"
            )
            logger.info(
                f"Thread {thread_id} (Session ID: {session_id}) end of thread cnt = {cnt}"
            )
            session.close()
        except Exception as e:
            logger.error(
                f"Thread {thread_id} (Session ID: {session_id}) encountered an error: {e}"
            )
            session.close()


# 기본값을 가지는 post의 row를 생성하는 함수
def create_default_post(session: Session):
    # 이미 존재하는지 확인
    post = session.query(Post).filter(Post.pk == 1).first()
    if not post:
        # 기본값으로 새로운 Post 레코드 생성
        new_post = Post(like=0)  # 예시로 pk가 1인 새로운 post 생성
        session.add(new_post)
        session.commit()


@core_router.get("/init")
def initialize_likes(session: Session = Depends(get_db)):
    post = session.query(Post).filter(Post.pk == 1).first()
    if post:
        post.like = 0
        post.version = 0
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

    t1 = threading.Thread(target=increase_like, args=(next(get_db()),))
    t2 = threading.Thread(target=increase_like, args=(next(get_db()),))

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


@core_router.get("/2th-plock")
def concurrent_increment_pessimistic_lock(session: Session = Depends(get_db)):

    create_default_post(session)

    t1 = threading.Thread(
        target=increase_like_with_pessimistic_lock, args=(next(get_db()),)
    )
    t2 = threading.Thread(
        target=increase_like_with_pessimistic_lock, args=(next(get_db()),)
    )
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    post = session.query(Post).filter(Post.pk == 1).first()
    result = post.like if post else 0

    return {
        "message": "/2th-plock : pessimistic lock increment completed",
        "like_result": result,
    }


@core_router.get("/2th-olock")
def increment_likes_optimistic_lock(session: Session = Depends(get_db)):
    # post 테이블이 비어있으면 기본값을 가지는 post의 row 생성
    create_default_post(session)

    t1 = threading.Thread(
        target=increase_like_by_optimistic_lock, args=(next(get_db()),)
    )
    t2 = threading.Thread(
        target=increase_like_by_optimistic_lock, args=(next(get_db()),)
    )
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    post = session.query(Post).filter(Post.pk == 1).first()
    result = post.like if post else 0

    return {
        "message": "/2th-olock : optimistic lock increment completed",
        "like_result": result,
    }


@core_router.get("/2th-olock-sqlalchemy-versioning")
def increment_likes_optimistic_lock_sqlqlchemy_versioning(
    session: Session = Depends(get_db),
):
    # post 테이블이 비어있으면 기본값을 가지는 post의 row 생성
    create_default_post(session)

    t1 = threading.Thread(
        target=increase_like_by_optimistic_lock_sqlalchemy_versioning,
        args=(next(get_db()),),
    )
    t2 = threading.Thread(
        target=increase_like_by_optimistic_lock_sqlalchemy_versioning,
        args=(next(get_db()),),
    )
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    post = session.query(Post).filter(Post.pk == 1).first()
    result = post.like if post else 0

    return {
        "message": "/2th-olock-sqlalchemy-versioning : optimistic lock increment completed",
        "like_result": result,
    }
