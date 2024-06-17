from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    Dependency that provides a SQLAlchemy database session.
    
    This function creates a new database session and ensures that it is properly closed after use.
    
    :yield: The database session.
    :rtype: SessionLocal
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

