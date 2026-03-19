"""爬取任务接口"""

import json
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth import get_current_user
from server.models import ScrapeTask
from server.schemas import TaskCreate, TaskOut, TaskListResponse
from server.services.scraper import start_scrape_task

router = APIRouter(prefix="/api/tasks", tags=["爬取任务"])


def _task_to_out(task: ScrapeTask) -> TaskOut:
    return TaskOut(
        id=task.id,
        keywords=task.get_keywords(),
        regions=task.get_regions(),
        status=task.status,
        total_found=task.total_found or 0,
        new_added=task.new_added or 0,
        progress=task.progress or 0,
        total_steps=task.total_steps or 0,
        started_at=task.started_at,
        finished_at=task.finished_at,
        error_msg=task.error_msg or "",
    )


@router.post("", response_model=TaskOut)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    if not data.keywords or not data.regions:
        raise HTTPException(status_code=400, detail="关键词和地区不能为空")

    task = ScrapeTask(
        keywords=json.dumps(data.keywords, ensure_ascii=False),
        regions=json.dumps(data.regions, ensure_ascii=False),
        status="pending",
        total_steps=len(data.keywords) * len(data.regions),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 启动后台爬取
    start_scrape_task(task.id)

    return _task_to_out(task)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    total = db.query(ScrapeTask).count()
    items = (
        db.query(ScrapeTask)
        .order_by(ScrapeTask.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return TaskListResponse(
        items=[_task_to_out(t) for t in items],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    task = db.query(ScrapeTask).filter(ScrapeTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _task_to_out(task)
