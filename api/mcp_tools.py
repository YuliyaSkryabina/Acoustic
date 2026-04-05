"""
Регистрация MCP-инструментов для интеграции с Claude Code.
5 инструментов согласно спецификации.
"""
from __future__ import annotations

from typing import Any

from core.engine import calculate as calc_engine
from core.models import CalcRequest, NoiseSource, CalcPoint, Screen


def register_mcp_tools(mcp):
    """Зарегистрировать все инструменты на MCP-сервере."""

    @mcp.tool()
    async def calculate_noise(
        sources: list[dict],
        points: list[dict],
        screens: list[dict] | None = None,
        temperature: float = 20.0,
        humidity: float = 70.0,
    ) -> dict:
        """
        Рассчитать уровни шума в расчётных точках от набора источников.

        Args:
            sources: Список источников шума. Каждый содержит:
                     id, lw_octave (8 значений), x, y, z, source_type (point/line)
            points:  Список расчётных точек: id, x, y, z, territory_type
            screens: Список экранов-барьеров: id, x1, y1, x2, y2, height
            temperature: Температура воздуха °C (по умолчанию 20)
            humidity: Относительная влажность % (по умолчанию 70)

        Returns:
            Объект CalcResponse с results (уровни по точкам и периодам) и isolines.
        """
        request = CalcRequest(
            sources=[NoiseSource.model_validate(s) for s in sources],
            points=[CalcPoint.model_validate(p) for p in points],
            screens=[Screen.model_validate(s) for s in (screens or [])],
            temperature=temperature,
            humidity=humidity,
        )
        response = calc_engine(request)
        return response.model_dump()

    @mcp.tool()
    async def get_sources(project_id: str) -> list[dict]:
        """
        Получить список источников шума активного проекта из базы данных.

        Args:
            project_id: Идентификатор проекта

        Returns:
            Список объектов NoiseSource
        """
        from api.database import get_sources as db_get_sources
        return await db_get_sources(project_id)

    @mcp.tool()
    async def add_source(project_id: str, source: dict) -> dict:
        """
        Добавить источник шума в проект.

        Args:
            project_id: Идентификатор проекта
            source: Объект NoiseSource (id, lw_octave, x, y, z, source_type, ...)

        Returns:
            {"status": "ok", "id": source_id}
        """
        from api.database import save_source
        src = NoiseSource.model_validate(source)
        await save_source(project_id, src.model_dump())
        return {"status": "ok", "id": src.id}

    @mcp.tool()
    async def export_to_qgis(project_id: str) -> dict:
        """
        Экспортировать данные проекта в GeoJSON для QGIS.

        Args:
            project_id: Идентификатор проекта

        Returns:
            {"sources": GeoJSON FeatureCollection, "results": GeoJSON FeatureCollection}
        """
        from api.database import get_sources as db_sources, get_results as db_results
        sources = await db_sources(project_id)
        results = await db_results(project_id)
        return {
            "project_id": project_id,
            "sources_count": len(sources),
            "results_count": len(results),
            "sources_geojson": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [s["x"], s["y"]]},
                        "properties": s,
                    }
                    for s in sources
                ],
            },
        }

    @mcp.tool()
    async def get_report(
        project_id: str,
        format: str = "json",
    ) -> dict:
        """
        Сформировать и получить отчёт по результатам расчёта.

        Args:
            project_id: Идентификатор проекта
            format: Формат отчёта: "json", "docx", "pdf"

        Returns:
            Для json: {"report": "...JSON строка..."}
            Для docx/pdf: {"file_path": "путь к файлу"}
        """
        from api.database import get_results as db_results
        from api.report_generator import generate_json_report, generate_docx_report, generate_pdf_report
        from core.models import PointResult, CalcResponse
        import tempfile

        results_data = await db_results(project_id)
        if not results_data:
            return {"error": "Результаты не найдены. Выполните расчёт сначала."}

        results = [PointResult.model_validate(r) for r in results_data]
        response = CalcResponse(results=results)

        if format == "json":
            return {"report": generate_json_report(response, project_id)}
        elif format == "docx":
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                path = f.name
            generate_docx_report(response, path, project_id)
            return {"file_path": path}
        elif format == "pdf":
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                path = f.name
            generate_pdf_report(response, path, project_id)
            return {"file_path": path}
        else:
            return {"error": f"Неизвестный формат: {format}"}
