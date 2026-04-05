"""POST /calculate_noise/ — главный расчётный endpoint."""
from fastapi import APIRouter

from core.engine import calculate as calc_engine
from core.models import CalcRequest, CalcResponse

router = APIRouter(prefix="/calculate_noise", tags=["calculation"])


@router.post("/", response_model=CalcResponse)
async def calculate_noise(request: CalcRequest) -> CalcResponse:
    """
    Рассчитать уровни шума в расчётных точках.

    Принимает источники шума и расчётные точки,
    возвращает матрицу результатов (день/ночь) и изолинии.
    """
    return calc_engine(request)
