from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from db_models.pipeline_stat import PipelineStat
from db_models.scrape_task import ScrapeTask
from schemas.pipeline import PipelineResponse

router = APIRouter(tags=["pipeline"])


@router.get("/{task_id}", response_model=PipelineResponse)
async def get_pipeline_stats(task_id: str, db: AsyncSession = Depends(get_db)):
    task_q = await db.execute(select(ScrapeTask).where(ScrapeTask.id == task_id))
    if not task_q.scalar_one_or_none():
        raise HTTPException(404, "Task not found")
    q = select(PipelineStat).where(PipelineStat.task_id == task_id).order_by(PipelineStat.created_at)
    result = await db.execute(q)
    return PipelineResponse(task_id=task_id, stages=result.scalars().all())
