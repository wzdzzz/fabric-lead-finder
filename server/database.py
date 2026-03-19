"""数据库配置 - SQLAlchemy + SQLite"""

import os
import sys

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from paths import DATA_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "leads.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from server.models import Lead, ScrapeTask  # noqa: F401 - ensure models registered
    Base.metadata.create_all(bind=engine)
