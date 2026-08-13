"""
The application entry point.

Wires together: static files, session cookies (so onboarding remembers
you across steps), the page routes (splash, login), the onboarding routes,
and the health checks.

Run:   uv run uvicorn app.main:app --reload
Open:  http://localhost:8000
"""

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, engine, get_db

# Import models so SQLAlchemy registers the tables before create_all runs.
from app.models import user as _user_model  # noqa: F401

# Routers (grouped route files).
from app.routers import pages, onboarding


app = FastAPI(title="VYROX")

# Signed session cookie. Uses SECRET_KEY from .env. This is how onboarding
# remembers which user you are between step 1 and later steps.
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Create tables directly for now (Alembic migrations replace this later).
Base.metadata.create_all(bind=engine)

# Serve CSS/JS/images.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register the page and onboarding routes.
app.include_router(pages.router)
app.include_router(onboarding.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "VYROX"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
