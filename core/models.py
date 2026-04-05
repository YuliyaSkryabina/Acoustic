"""
Pydantic v2 модели данных — единственный контракт между всеми слоями.
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class SourceType(str, Enum):
    POINT = "point"
    LINE = "line"


class TerritoryType(str, Enum):
    RESIDENTIAL = "residential"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    RECREATION = "recreation"
    INDUSTRIAL = "industrial"
    OFFICE = "office"


class NoiseSource(BaseModel):
    id: str
    source_type: SourceType = SourceType.POINT
    description: str = ""
    is_permanent: bool = True
    # Октавные уровни звуковой мощности Lw [дБ], 63..8000 Гц
    lw_octave: list[float] = Field(..., min_length=8, max_length=8)
    x: float
    y: float
    z: float = 1.0  # высота источника над землёй [м]
    # Для линейного ИШ — координаты второй точки
    x2: Optional[float] = None
    y2: Optional[float] = None
    duration_day: float = 16.0    # время работы днём [ч]
    duration_night: float = 8.0   # время работы ночью [ч]
    directionality: float = 0.0   # ΔL_ф — поправка на направленность [дБ]


class CalcPoint(BaseModel):
    id: str
    x: float
    y: float
    z: float = 1.5  # высота расчётной точки над землёй [м]
    territory_type: TerritoryType = TerritoryType.RESIDENTIAL
    description: str = ""


class Screen(BaseModel):
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    height: float   # высота экрана [м]
    absorption: float = 0.0  # коэффициент поглощения (0 — жёсткий, 1 — мягкий)


class CalcRequest(BaseModel):
    sources: list[NoiseSource]
    points: list[CalcPoint]
    screens: list[Screen] = []
    temperature: float = 20.0    # температура воздуха [°C]
    humidity: float = 70.0       # относительная влажность [%]
    ground_type: float = 0.0     # G: 0=асфальт, 1=трава/грунт


class PointResult(BaseModel):
    point_id: str
    period: Literal["day", "night"]
    l_octave: list[float] = Field(..., min_length=8, max_length=8)
    l_a_eq: float    # эквивалентный уровень [дБА]
    l_a_max: float   # максимальный уровень [дБА]
    pdu_eq: float    # ПДУ эквивалентного уровня [дБА]
    pdu_max: float   # ПДУ максимального уровня [дБА]
    exceeded: bool
    exceedance_eq: float   # превышение ПДУ [дБА]; отрицательное = норма


class IsolineFeature(BaseModel):
    level_dba: float
    coordinates: list[list[float]]  # [[x1,y1],[x2,y2],...]


class CalcResponse(BaseModel):
    results: list[PointResult]
    isolines: list[IsolineFeature] = []
    metadata: dict = {}
