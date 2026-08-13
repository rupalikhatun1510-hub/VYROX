"""
The application entry point.

This wires FastAPI together: it registers the database tables, mounts
the static files folder, and defines a first health-check route so you
can confirm the whole stack is alive in your browser.

Run it with:  uv run uvicorn app.main:app --reload
Then open:     http://localhost:8000
"""

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db

# Import models so SQLAlchemy knows about them before creating tables.
# (Even though we don't call User directly here, importing registers it.)
from app.models import user as _user_model  # noqa: F401


# Create the FastAPI application object.
app = FastAPI(title="VYROX")

# For the very first run we let SQLAlchemy create tables directly.
# Later, Alembic migrations replace this line. Kept simple for now so
# you get a working app before learning migrations.
Base.metadata.create_all(bind=engine)

# Serve files in app/static at the URL /static (CSS, JS, images).
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health():
    """A simple 'is the app running?' check. Returns JSON."""
    return {"status": "ok", "app": "VYROX"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """
    Confirms the app can actually talk to Postgres.
    Runs the trivial query 'SELECT 1' and reports success.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
