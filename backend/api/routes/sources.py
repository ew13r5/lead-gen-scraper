from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["sources"])

AVAILABLE_SOURCES = [
    {"name": "yellowpages", "display_name": "Yellow Pages", "renderer": "static", "proxy_required": True},
    {"name": "yelp", "display_name": "Yelp", "renderer": "static", "proxy_required": True},
    {"name": "bbb", "display_name": "Better Business Bureau", "renderer": "static", "proxy_required": False},
    {"name": "clutch", "display_name": "Clutch", "renderer": "static", "proxy_required": False},
    {"name": "crunchbase", "display_name": "Crunchbase", "renderer": "playwright", "proxy_required": True},
]
SOURCE_NAMES = {s["name"] for s in AVAILABLE_SOURCES}


@router.get("/")
async def list_sources():
    return AVAILABLE_SOURCES


@router.post("/{name}/validate")
async def validate_source(name: str):
    if name not in SOURCE_NAMES:
        raise HTTPException(404, f"Source '{name}' not found")
    return {"valid": True, "source": name}
