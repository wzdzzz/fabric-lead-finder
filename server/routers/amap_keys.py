"""高德 Key 管理接口"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth import get_current_user
from server.models import AmapKey
from server.schemas import AmapKeyCreate, AmapKeyOut

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


def get_active_key(db: Session) -> str | None:
    """获取当前可用的 key，自动切换用完的 key"""
    current_month = datetime.now().strftime("%Y-%m")

    keys = db.query(AmapKey).order_by(AmapKey.id).all()
    if not keys:
        return None

    # 重置过期月份的计数
    for k in keys:
        if k.reset_month != current_month:
            k.used_count = 0
            k.reset_month = current_month
    db.commit()

    # 先尝试当前激活的 key
    active = db.query(AmapKey).filter(AmapKey.is_active == True).first()
    if active and active.used_count < active.monthly_limit:
        return active.key

    # 当前 key 用完了，找下一个可用的
    for k in keys:
        if k.used_count < k.monthly_limit:
            # 切换到这个 key
            db.query(AmapKey).update({AmapKey.is_active: False})
            k.is_active = True
            db.commit()
            return k.key

    return None  # 所有 key 都用完了


def increment_key_usage(db: Session, key_value: str):
    """增加 key 使用次数"""
    key = db.query(AmapKey).filter(AmapKey.key == key_value).first()
    if key:
        key.used_count += 1
        db.commit()
