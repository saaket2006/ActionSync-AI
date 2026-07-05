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
    """Initializes the database schema and runs migrations using Alembic."""
    import os
    import logging
    from alembic.config import Config
    from alembic import command

    logger = logging.getLogger("actionsync.database")
    logger.info("Running database migrations...")
    
    try:
        # Resolve absolute paths relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ini_path = os.path.join(base_dir, "alembic.ini")
        migrations_dir = os.path.join(base_dir, "migrations")
        
        # Load Alembic Config
        alembic_cfg = Config(ini_path)
        alembic_cfg.set_main_option("script_location", migrations_dir)
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        # Run upgrade command programmatically
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully.")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        # Fallback to direct metadata creation in case of migrations failure
        logger.warning("Falling back to Base.metadata.create_all()")
        import database.models
        Base.metadata.create_all(bind=engine)

def get_db():
    """Yields a database session context, ensuring proper cleanup."""
    db = db_session()
    try:
        yield db
    finally:
        db.close()
