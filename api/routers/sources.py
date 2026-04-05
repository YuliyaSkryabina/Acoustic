"""GET/POST /sources/ — управление источниками шума проекта."""
from fastapi import APIRouter, HTTPException

from api.database import get_sources, save_source
from core.models import NoiseSource

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/")
async def list_sources(project_id: str) -> list[dict]:
    """Получить список источников шума активного проекта."""
    return await get_sources(project_id)


@router.post("/")
async def add_source(project_id: str, source: NoiseSource) -> dict:
    """Добавить источник шума в проект."""
    await save_source(project_id, source.model_dump())
    return {"status": "ok", "id": source.id}
