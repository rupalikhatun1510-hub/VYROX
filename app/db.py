"""
Sets up the connection to Postgres and gives every request its own
short-lived database session.

Think of the 'engine' as the pipe to the database, and a 'session' as
one conversation over that pipe that opens when a request starts and
closes when it ends.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings


# The engine is the low-level connection pool to Postgres.
# pool_pre_ping checks a connection is still alive before using it,
# which avoids "server closed the connection" errors after idle time.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# A factory that produces new Session objects.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """
    Every database table (model) will inherit from this class.
    SQLAlchemy uses it to keep track of all your tables.
    """
    pass


def get_db():
    """
    FastAPI dependency. For each request it opens a session, hands it to
    the route, and guarantees the session is closed afterwards even if
    the route raises an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
