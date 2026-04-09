"""数据库会话与初始化。"""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Declarative Base。"""


engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """依赖注入：每次请求分配一个数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

