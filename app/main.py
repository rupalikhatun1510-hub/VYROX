from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import settings
from app.db import Base, engine, get_db
from app.models import user as _user_model  # noqa: F401
from app.routers import pages, onboarding
app = FastAPI(title="VYROX")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(onboarding.router)
@app.get("/health")
def health():
    return {"status": "ok", "app": "VYROX"}
@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
