"""Pydantic 请求/响应模型"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# === Auth ===
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str


# === Lead ===
class LeadOut(BaseModel):
    id: int
    name: str
    phone: str
    city: str
    district: str
    address: str
    region: str
    industry: str
    location: str
    source: str
    search_keyword: str
    search_region: str
    status: str
    tags: list[str]
    notes: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class LeadBatchUpdate(BaseModel):
    ids: list[int]
    status: Optional[str] = None
    add_tags: Optional[list[str]] = None
    remove_tags: Optional[list[str]] = None


class LeadListResponse(BaseModel):
    items: list[LeadOut]
    total: int
    page: int
    page_size: int


class LeadStats(BaseModel):
    total: int
    with_phone: int
    without_phone: int
    by_status: dict[str, int]
    by_city: dict[str, int]


# === Scrape Task ===
class TaskCreate(BaseModel):
    keywords: list[str]
    regions: list[str]


class TaskOut(BaseModel):
    id: int
    keywords: list[str]
    regions: list[str]
    status: str
    total_found: int
    new_added: int
    progress: int
    total_steps: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_msg: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskOut]
    total: int


# === Export ===
class ExportRequest(BaseModel):
    city: Optional[str] = None
    status: Optional[str] = None
    tag: Optional[str] = None
    search: Optional[str] = None


# === Config ===
class ConfigResponse(BaseModel):
    keywords: list[str]
    regions: list[str]
