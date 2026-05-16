from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",  # SQL logs in dev only
    pool_pre_ping=True,                       # auto-reconnect
    pool_size=10,
    max_overflow=20,
)


def create_db_and_tables():
    """Run once at startup to create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency — yields a DB session per request."""
    with Session(engine) as session:
        yield session
