import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import get_config

def get_engine():
    """Inisialisasi engine PostgreSQL berdasarkan konfigurasi dan API Key."""
    db_cfg = get_config().db
    uri = db_cfg.postgres_uri
    api_key = db_cfg.postgres_api_key

    connect_args = {}
    if uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    elif api_key:
        # Jika menggunakan API key cloud database (seperti Supabase/Neon API Key / SSL Option)
        connect_args["options"] = f"-c apikey={api_key}"

    return create_engine(uri, connect_args=connect_args)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Generator session database PostgreSQL untuk Dependency Injection FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_postgres():
    """Membuat tabel jika belum ada."""
    Base.metadata.create_all(bind=engine)
