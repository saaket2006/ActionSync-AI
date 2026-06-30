from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import settings

# For SQLite, check_same_thread=False is required for multi-threaded systems like FastAPI/Streamlit
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()

def init_db():
    """Initializes the database schema by creating all tables."""
    import database.models  # Import models to register on Base
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yields a database session context, ensuring proper cleanup."""
    db = db_session()
    try:
        yield db
    finally:
        db.close()
