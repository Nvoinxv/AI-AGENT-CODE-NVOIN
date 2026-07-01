import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ambil URI dari environment variable dengan fallback ke SQLite lokal jika Postgres belum berjalan di terminal lokal
POSTGRES_URI = os.getenv("POSTGRES_URI", "sqlite:///./nvoin_local.db")

# Inisialisasi engine
engine = create_engine(
    POSTGRES_URI,
    connect_args={"check_same_thread": False} if POSTGRES_URI.startswith("sqlite") else {}
)

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
