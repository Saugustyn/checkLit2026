from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite - plik lokalny, zero konfiguracji
SQLALCHEMY_DATABASE_URL = "sqlite:///./literary_analyzer.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do wstrzykiwania sesji DB w routerach FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
