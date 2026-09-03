"""
Database configuration and session management.
Supports PostgreSQL (default in Docker) with automatic graceful fallback to SQLite for local development.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Use SQLite for local development by default
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "pharmacy_db.sqlite3")
    DATABASE_URL = f"sqlite:///{db_path}"

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    # Fallback to local SQLite if remote PostgreSQL is unreachable
    print(f"[WARN] Failed to connect to {DATABASE_URL}. Falling back to SQLite: {e}")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "pharmacy_db.sqlite3")
    DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
