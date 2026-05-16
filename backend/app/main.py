from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.apps import router as apps_router
from app.api.incidents import router as incidents_router
from app.api.auth import router as auth_router

# Import all models so SQLModel sees them at startup
from app.models import App, UserRating, HarmReport, GuardianScore, Incident, User  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    create_db_and_tables()

    # One-time migration: add user columns if missing (safe to re-run, silently ignored if exists)
    from app.core.database import engine
    from sqlmodel import Session, text
    migrations = [
        "ALTER TABLE userrating ADD COLUMN user_id INTEGER",
        "ALTER TABLE userrating ADD COLUMN user_name VARCHAR",
        "ALTER TABLE harmreport ADD COLUMN user_id INTEGER",
        "ALTER TABLE harmreport ADD COLUMN user_name VARCHAR",
        "ALTER TABLE incident ADD COLUMN user_id INTEGER",
        "ALTER TABLE incident ADD COLUMN user_name VARCHAR",
    ]
    with Session(engine) as session:
        for sql in migrations:
            try:
                session.exec(text(sql))
            except Exception:
                pass  # column already exists
        session.commit()

    yield


app = FastAPI(
    title="GX-project",
    description="Verify, rate, and report harm from any AI app",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev mode — allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(apps_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

