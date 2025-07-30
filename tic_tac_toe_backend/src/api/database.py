import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# PUBLIC_INTERFACE
def get_db_url():
    """
    Returns the database URL from DB_URL environment variable.
    """
    db_url = os.environ.get("DB_URL")
    if not db_url:
        raise RuntimeError("DB_URL environment variable not set")
    return db_url

SQLALCHEMY_DATABASE_URL = get_db_url()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# PUBLIC_INTERFACE
def init_db():
    """
    PUBLIC_INTERFACE
    Initializes database tables if they do not exist.
    """
    Base.metadata.create_all(bind=engine)

# PUBLIC_INTERFACE
def get_db():
    """
    PUBLIC_INTERFACE
    Dependency for FastAPI to get SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
