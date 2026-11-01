import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL = os.getenv("MEMORA_DATABASE_URL", "sqlite:///./memora.db")
if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql+psycopg://", 1)
elif URL.startswith("postgresql://"):
    URL = URL.replace("postgresql://", "postgresql+psycopg://", 1)
if os.getenv("MEMORA_ENV", "development").lower() == "production" and URL.startswith("sqlite"):
    raise RuntimeError("Production requires a persistent PostgreSQL MEMORA_DATABASE_URL")
connect_args = {"check_same_thread": False} if URL.startswith("sqlite") else {}
engine = create_engine(URL, connect_args=connect_args, pool_pre_ping=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
