from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_mode
from db_models.scrape_task import ScrapeTask
from schemas.task import TaskCreate, TaskListResponse, TaskResponse
from tasks.scrape_task import run_scrape

router = APIRouter(tags=["tasks"])

KNOWN_SOURCES = {"yellowpages", "yelp", "bbb", "clutch"}


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    mode: str = Depends(get_current_mode),
):
    if body.source not in KNOWN_SOURCES:
        raise HTTPException(400, f"Unknown source: {body.source}")
    task = ScrapeTask(
        source=body.source, query=body.query, location=body.location,
        limit=body.limit, enrich=body.enrich, mode=mode, status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    run_scrape.delay(task.id)
    return task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db),
):
    total_q = await db.execute(select(func.count(ScrapeTask.id)))
    total = total_q.scalar() or 0
    q = select(ScrapeTask).order_by(ScrapeTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = result.scalars().all()
    return TaskListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapeTask).where(ScrapeTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapeTask).where(ScrapeTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status in ("pending", "running"):
        task.status = "cancelled"
        await db.commit()
        await db.refresh(task)
    return task
