"""
Database initialization and session factory.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import config

Base = declarative_base()

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables."""
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield a session (context manager)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
