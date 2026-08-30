from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.database.base import Base

_engine = None
_session_factory = None


def get_engine():
    global _engine

    if _engine is None:
        settings = get_settings()
        url = settings.database_url

        # Use psycopg3 for PostgreSQL
        if url.startswith("postgresql://"):
            url = url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )

        kwargs = {
            "future": True,
            "pool_pre_ping": True,
        }

        if url.startswith("sqlite"):
            kwargs["connect_args"] = {
                "check_same_thread": False
            }
        else:
            # Railway is a persistent server, so reuse PostgreSQL
            # connections instead of creating a new connection per request.
            kwargs["pool_size"] = 5
            kwargs["max_overflow"] = 5
            kwargs["pool_recycle"] = 1800

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

    settings = get_settings()

    if settings.database_url.startswith("sqlite"):
        # Auto-create tables for local development and tests.
        Base.metadata.create_all(bind=get_engine())
    else:
        # PostgreSQL production schema is managed separately
        # through Supabase SQL/migrations.
        pass


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