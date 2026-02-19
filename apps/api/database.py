from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Fix Render's "postgres://" schema to "postgresql://" for SQLAlchemy 1.4+
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args=connect_args
    )
else:
    # Postgres Configuration
    # internal (Render) or external (Supabase) often require SSL
    # We enforce sslmode=require if not present (unless explicitly disabled)
    if "sslmode" not in SQLALCHEMY_DATABASE_URL:
        connect_args = {"sslmode": "require"}
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True  # Vital for handling dropped connections
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
