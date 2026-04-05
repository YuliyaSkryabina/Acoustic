"""POST /export_to_qgis/ — экспорт данных для QGIS."""
import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.database import get_sources, get_results
from core.models import NoiseSource

router = APIRouter(prefix="/export_to_qgis", tags=["export"])


@router.post("/")
async def export_to_qgis(project_id: str) -> dict:
    """
    Экспортировать данные проекта в GeoJSON формат для QGIS.
    Возвращает два GeoJSON FeatureCollection:
    - sources: источники шума как точки
    - results: расчётные точки с атрибутами уровней
    """
    sources_data = await get_sources(project_id)
    results_data = await get_results(project_id)

    # GeoJSON для источников
    sources_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [s["x"], s["y"]]},
                "properties": {
                    "id": s["id"],
                    "description": s.get("description", ""),
                    "source_type": s.get("source_type", "point"),
                    "lw_octave": s.get("lw_octave", []),
                },
            }
            for s in sources_data
        ],
    }

    # GeoJSON для результатов
    results_by_point: dict = {}
    for r in results_data:
        pid = r["point_id"]
        if pid not in results_by_point:
            results_by_point[pid] = {}
        results_by_point[pid][r["period"]] = r

    results_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},  # координаты нужно хранить в РТ
                "properties": {
                    "id": pid,
                    "l_a_eq_day": periods.get("day", {}).get("l_a_eq"),
                    "l_a_eq_night": periods.get("night", {}).get("l_a_eq"),
                    "exceeded_day": periods.get("day", {}).get("exceeded"),
                    "exceeded_night": periods.get("night", {}).get("exceeded"),
                },
            }
            for pid, periods in results_by_point.items()
        ],
    }

    return {
        "sources": sources_geojson,
        "results": results_geojson,
        "project_id": project_id,
    }
