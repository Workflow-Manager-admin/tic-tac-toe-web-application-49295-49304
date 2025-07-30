import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# PUBLIC_INTERFACE
def get_db_url():
    """
    Returns the database URL from DB_URL environment variable, or uses SQLite by default.
    """
    db_url = os.environ.get("DB_URL")
    if not db_url:
        # Default to SQLite in local file
        db_url = "sqlite:///./tic_tac_toe.db"
    return db_url

SQLALCHEMY_DATABASE_URL = get_db_url()

# For SQLite, connect_args needed to handle multithreading in FastAPI/dev server
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
)

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
