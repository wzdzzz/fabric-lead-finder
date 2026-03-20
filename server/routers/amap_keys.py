"""高德 Key 管理接口"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth import get_current_user
from server.models import AmapKey
from server.schemas import AmapKeyCreate, AmapKeyUpdate, AmapKeyOut

router = APIRouter(prefix="/api/amap-keys", tags=["高德Key管理"])


def _check_reset(key: AmapKey):
    """按月重置用量计数"""
    current_month = datetime.now().strftime("%Y-%m")
    if key.reset_month != current_month:
        key.used_count = 0
        key.reset_month = current_month


@router.get("", response_model=list[AmapKeyOut])
def list_keys(
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    keys = db.query(AmapKey).order_by(AmapKey.id).all()
    for k in keys:
        _check_reset(k)
    db.commit()
    return keys


@router.post("", response_model=AmapKeyOut)
def add_key(
    data: AmapKeyCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    existing = db.query(AmapKey).filter(AmapKey.key == data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="该 Key 已存在")

    # 如果是第一个 key，自动设为激活
    count = db.query(AmapKey).count()
    key = AmapKey(
        key=data.key,
        name=data.name or f"Key-{count + 1}",
        is_active=count == 0,
        monthly_limit=data.monthly_limit,
        used_count=data.used_count,
        reset_month=datetime.now().strftime("%Y-%m"),
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@router.put("/{key_id}/activate", response_model=AmapKeyOut)
def activate_key(
    key_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    key = db.query(AmapKey).filter(AmapKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key 不存在")

    # 取消其他 key 的激活状态
    db.query(AmapKey).update({AmapKey.is_active: False})
    key.is_active = True
    db.commit()
    db.refresh(key)
    return key


@router.put("/{key_id}", response_model=AmapKeyOut)
def update_key(
    key_id: int,
    data: AmapKeyUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    key = db.query(AmapKey).filter(AmapKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key 不存在")

    if data.name is not None:
        key.name = data.name
    if data.monthly_limit is not None:
        key.monthly_limit = data.monthly_limit
    if data.used_count is not None:
        key.used_count = data.used_count

    db.commit()
    db.refresh(key)
    return key


@router.delete("/{key_id}")
def delete_key(
    key_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    key = db.query(AmapKey).filter(AmapKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key 不存在")
    was_active = key.is_active
    db.delete(key)
    db.commit()

    # 如果删除的是激活的 key，自动激活第一个
    if was_active:
        first = db.query(AmapKey).order_by(AmapKey.id).first()
        if first:
            first.is_active = True
            db.commit()

    return {"detail": "已删除"}
