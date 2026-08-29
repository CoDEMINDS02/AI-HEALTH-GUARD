from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.database.base import Base

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        url = settings.database_url
        kwargs = {"future": True}
        if url.startswith("sqlite"):
            kwargs["pool_pre_ping"] = True
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            # Serverless (Vercel): use NullPool so each invocation gets a fresh
            # connection and releases it on completion. This avoids idle pooled
            # connections holding open Supabase Transaction Pooler slots.
            kwargs["poolclass"] = NullPool
        _engine = create_engine(url, **kwargs)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    return _session_factory


def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def reset_engine() -> None:
    global _engine, _session_factory
    _engine = None
    _session_factory = None


def get_db():
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
