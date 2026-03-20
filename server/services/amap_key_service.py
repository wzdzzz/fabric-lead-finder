"""高德 Key 服务 - 获取可用 key、增加用量"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from server.models import AmapKey


def get_active_key(db: Session) -> Optional[str]:
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
