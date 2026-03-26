from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from db_models.company import Company
from schemas.company import CompanyListResponse, CompanyResponse

router = APIRouter(tags=["results"])

SORT_FIELDS = {"company_name", "created_at", "source", "city", "state", "rating"}


@router.get("/", response_model=CompanyListResponse)
async def list_results(
    task_id: str | None = None,
    source: str | None = None,
    city: str | None = None,
    state: str | None = None,
    category: str | None = None,
    has_email: bool | None = None,
    has_phone: bool | None = None,
    needs_review: bool | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    if sort_by not in SORT_FIELDS:
        raise HTTPException(400, f"Invalid sort_by. Allowed: {SORT_FIELDS}")

    q = select(Company).where(Company.is_duplicate_of.is_(None))
    if task_id:
        q = q.where(Company.task_id == task_id)
    if source:
        q = q.where(Company.source == source)
    if city:
        q = q.where(Company.city == city)
    if state:
        q = q.where(Company.state == state)
    if category:
        q = q.where(Company.category == category)
    if has_email is True:
        q = q.where(Company.email.isnot(None))
    elif has_email is False:
        q = q.where(Company.email.is_(None))
    if has_phone is True:
        q = q.where(Company.phone_normalized.isnot(None))
    elif has_phone is False:
        q = q.where(Company.phone_normalized.is_(None))
    if needs_review is not None:
        q = q.where(Company.needs_review == needs_review)
    if search:
        pattern = f"%{search}%"
        q = q.where(or_(
            Company.company_name.ilike(pattern),
            Company.email.ilike(pattern),
            Company.phone.ilike(pattern),
        ))

    count_q = select(func.count()).select_from(q.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    col = getattr(Company, sort_by)
    order = col.desc() if sort_order == "desc" else col.asc()
    q = q.order_by(order).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    items = result.scalars().all()
    return CompanyListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_result(company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    return company
