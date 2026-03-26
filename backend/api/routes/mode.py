from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api.deps import _get_settings

router = APIRouter(tags=["mode"])


class ModeUpdate(BaseModel):
    mode: Literal["live", "demo"]


@router.get("/")
async def get_mode():
    return {"mode": _get_settings().app_mode}


@router.put("/")
async def set_mode(body: ModeUpdate):
    _get_settings().app_mode = body.mode
    return {"mode": body.mode}
