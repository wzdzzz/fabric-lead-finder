"""导出接口"""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from server.database import get_db
from server.auth import get_current_user
from server.models import Lead
from server.schemas import ExportRequest
from server.services.export import export_leads

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.post("")
def export_excel(
    data: ExportRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = db.query(Lead)

    if data.search:
        like = f"%{data.search}%"
        query = query.filter(or_(
            Lead.name.like(like),
            Lead.phone.like(like),
            Lead.address.like(like),
        ))
    if data.city:
        city_list = [c.strip() for c in data.city.split(',') if c.strip()]
        if len(city_list) == 1:
            query = query.filter(Lead.city == city_list[0])
        else:
            query = query.filter(Lead.city.in_(city_list))
    if data.status:
        query = query.filter(Lead.status == data.status)
    if data.tag:
        query = query.filter(Lead.tags.like(f'%"{data.tag}"%'))

    leads = query.all()
    filepath = export_leads(leads)

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filepath.split("/")[-1].split("\\")[-1],
    )
