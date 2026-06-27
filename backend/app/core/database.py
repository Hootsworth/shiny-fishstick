from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

connect_args = {}
extra_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    extra_args = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True
    }

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **extra_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
