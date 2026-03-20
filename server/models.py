"""数据库模型"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from server.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False, index=True)
    phone = Column(Text, default="")
    city = Column(Text, default="", index=True)
    district = Column(Text, default="")
    address = Column(Text, default="")
    region = Column(Text, default="")
    industry = Column(Text, default="")
    location = Column(Text, default="")
    source = Column(Text, default="")
    search_keyword = Column(Text, default="")
    search_region = Column(Text, default="")
    status = Column(Text, default="未联系", index=True)
    tags = Column(Text, default="[]")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, tag_list):
        self.tags = json.dumps(tag_list, ensure_ascii=False)


class ScrapeTask(Base):
    __tablename__ = "scrape_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keywords = Column(Text, default="[]")
    regions = Column(Text, default="[]")
    status = Column(Text, default="pending", index=True)
    total_found = Column(Integer, default=0)
    new_added = Column(Integer, default=0)
    progress = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    error_msg = Column(Text, default="")

    def get_keywords(self):
        try:
            return json.loads(self.keywords) if self.keywords else []
        except (json.JSONDecodeError, TypeError):
            return []

    def get_regions(self):
        try:
            return json.loads(self.regions) if self.regions else []
        except (json.JSONDecodeError, TypeError):
            return []


class AmapKey(Base):
    __tablename__ = "amap_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(Text, unique=True, nullable=False)
    name = Column(Text, default="")
    is_active = Column(Boolean, default=False)
    monthly_limit = Column(Integer, default=5000)
    used_count = Column(Integer, default=0)
    reset_month = Column(Text, default="")  # "2026-03" 格式，用于按月重置计数
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
