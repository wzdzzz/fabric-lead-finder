"""客户数据接口"""

import json
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from server.database import get_db
from server.auth import get_current_user
from server.models import Lead
from server.schemas import (
    LeadOut, LeadUpdate, LeadBatchUpdate,
    LeadListResponse, LeadStats,
)

router = APIRouter(prefix="/api/leads", tags=["客户数据"])


def _lead_to_out(lead: Lead) -> LeadOut:
    return LeadOut(
        id=lead.id,
        name=lead.name,
        phone=lead.phone or "",
        city=lead.city or "",
        district=lead.district or "",
        address=lead.address or "",
        region=lead.region or "",
        industry=lead.industry or "",
        location=lead.location or "",
        source=lead.source or "",
        search_keyword=lead.search_keyword or "",
        search_region=lead.search_region or "",
        status=lead.status or "未联系",
        tags=lead.get_tags(),
        notes=lead.notes or "",
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.get("", response_model=LeadListResponse)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="搜索公司名称/电话/地址"),
    city: str = Query("", description="按城市筛选，多个用逗号分隔"),
    status: str = Query("", description="按状态筛选"),
    tag: str = Query("", description="按标签筛选"),
    has_phone: str = Query("", description="有电话: yes/no"),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = db.query(Lead)

    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            Lead.name.like(like),
            Lead.phone.like(like),
            Lead.address.like(like),
        ))
    if city:
        city_list = [c.strip() for c in city.split(',') if c.strip()]
        if len(city_list) == 1:
            query = query.filter(Lead.city == city_list[0])
        else:
            query = query.filter(Lead.city.in_(city_list))
    if status:
        query = query.filter(Lead.status == status)
    if tag:
        query = query.filter(Lead.tags.like(f'%"{tag}"%'))
    if has_phone == "yes":
        query = query.filter(Lead.phone != "", Lead.phone.isnot(None))
    elif has_phone == "no":
        query = query.filter(or_(Lead.phone == "", Lead.phone.is_(None)))

    total = query.count()
    items = query.order_by(Lead.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return LeadListResponse(
        items=[_lead_to_out(lead) for lead in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/tags", response_model=list[str])
def get_all_tags(
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    leads = db.query(Lead.tags).filter(Lead.tags != "[]", Lead.tags != "").all()
    all_tags = set()
    for (tags_str,) in leads:
        try:
            tags = json.loads(tags_str) if tags_str else []
            all_tags.update(tags)
        except (json.JSONDecodeError, TypeError):
            pass
    return sorted(all_tags)


@router.get("/stats", response_model=LeadStats)
def get_stats(
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    total = db.query(func.count(Lead.id)).scalar() or 0
    with_phone = db.query(func.count(Lead.id)).filter(
        Lead.phone != "", Lead.phone.isnot(None)
    ).scalar() or 0

    # 按状态统计
    status_rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    by_status = {s: c for s, c in status_rows if s}

    # 按城市统计
    city_rows = db.query(Lead.city, func.count(Lead.id)).group_by(Lead.city).order_by(
        func.count(Lead.id).desc()
    ).all()
    by_city = {c: n for c, n in city_rows if c}

    return LeadStats(
        total=total,
        with_phone=with_phone,
        without_phone=total - with_phone,
        by_status=by_status,
        by_city=by_city,
    )


@router.put("/batch", response_model=dict)
def batch_update_leads(
    data: LeadBatchUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    leads = db.query(Lead).filter(Lead.id.in_(data.ids)).all()
    updated = 0

    for lead in leads:
        if data.status is not None:
            lead.status = data.status
        if data.add_tags:
            current = lead.get_tags()
            for t in data.add_tags:
                if t not in current:
                    current.append(t)
            lead.set_tags(current)
        if data.remove_tags:
            current = lead.get_tags()
            current = [t for t in current if t not in data.remove_tags]
            lead.set_tags(current)
        updated += 1

    db.commit()
    return {"updated": updated}


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="客户不存在")

    if data.phone is not None:
        lead.phone = data.phone
    if data.address is not None:
        lead.address = data.address
    if data.status is not None:
        lead.status = data.status
    if data.tags is not None:
        lead.set_tags(data.tags)
    if data.notes is not None:
        lead.notes = data.notes

    db.commit()
    db.refresh(lead)
    return _lead_to_out(lead)
