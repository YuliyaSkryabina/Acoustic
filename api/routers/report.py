"""GET /report — формирование отчётов."""
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

from api.database import get_sources, get_results
from api.report_generator import generate_json_report, generate_docx_report, generate_pdf_report
from core.engine import calculate
from core.models import CalcRequest, NoiseSource, CalcPoint, CalcResponse

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/")
async def get_report(
    project_id: str,
    format: str = Query("json", description="Формат: json, docx, pdf"),
    project_name: str = Query("Акустик", description="Название проекта"),
):
    """Сформировать и вернуть отчёт по проекту."""
    results_data = await get_results(project_id)
    if not results_data:
        raise HTTPException(404, "Результаты не найдены. Сначала выполните расчёт.")

    # Собрать CalcResponse из сохранённых результатов
    from core.models import PointResult
    results = [PointResult.model_validate(r) for r in results_data]
    response = CalcResponse(results=results)

    if format == "json":
        return JSONResponse(
            content={"report": generate_json_report(response, project_name)}
        )

    elif format == "docx":
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            path = f.name
        out = generate_docx_report(response, path, project_name)
        if not out:
            raise HTTPException(500, "Не удалось создать DOCX. Установите python-docx.")
        return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            filename=f"{project_name}.docx")

    elif format == "pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        out = generate_pdf_report(response, path, project_name)
        if not out:
            raise HTTPException(500, "Не удалось создать PDF. Установите reportlab.")
        return FileResponse(path, media_type="application/pdf",
                            filename=f"{project_name}.pdf")

    else:
        raise HTTPException(400, f"Неизвестный формат: {format}. Допустимые: json, docx, pdf")
