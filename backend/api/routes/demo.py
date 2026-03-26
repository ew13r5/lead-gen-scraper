from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_mode, get_db
from db_models.company import Company
from db_models.scrape_task import ScrapeTask

router = APIRouter(tags=["demo"])


class SeedRequest(BaseModel):
    count: int = 200
    sources: int = 3


@router.post("/seed")
async def seed_demo_data(body: SeedRequest, db: AsyncSession = Depends(get_db)):
    from demo import seed_demo, make_dirty
    from pipeline import PipelineRunner
    from pipeline.html_cleaner import HTMLCleaner
    from pipeline.field_validator import FieldValidator

    records = seed_demo(count=body.count, sources=body.sources)
    dirty = make_dirty(records)
    runner = PipelineRunner([HTMLCleaner(), FieldValidator(check_email_dns=False)])
    cleaned, _ = runner.run(dirty)

    task = ScrapeTask(source="demo", query="demo", location="demo", mode="demo", status="completed",
                      total_scraped=len(dirty), total_cleaned=len(cleaned))
    db.add(task)
    await db.commit()
    await db.refresh(task)

    for record in cleaned[:body.count]:
        db.add(Company(
            company_name=record.get("company_name", ""),
            phone=record.get("phone"), phone_normalized=record.get("phone_normalized"),
            email=record.get("email"), website=record.get("website"),
            address=record.get("address"), city=record.get("city"),
            state=record.get("state"), category=record.get("category"),
            source=record.get("source"), task_id=task.id,
        ))
    await db.commit()
    return {"task_id": task.id, "companies_created": min(len(cleaned), body.count)}


@router.post("/reset")
async def reset_demo_data(db: AsyncSession = Depends(get_db), mode: str = Depends(get_current_mode)):
    if mode != "demo":
        raise HTTPException(403, "Reset only available in demo mode")
    tasks_q = await db.execute(select(ScrapeTask.id).where(ScrapeTask.mode == "demo"))
    task_ids = [r[0] for r in tasks_q.all()]
    if task_ids:
        await db.execute(delete(Company).where(Company.task_id.in_(task_ids)))
        await db.execute(delete(ScrapeTask).where(ScrapeTask.id.in_(task_ids)))
        await db.commit()
    return {"deleted_tasks": len(task_ids)}
