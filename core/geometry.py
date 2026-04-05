"""
Геометрические расчёты: расстояния и геометрическое расхождение.
СП 51.13330.2011, разделы 7.3–7.4.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import NoiseSource, CalcPoint


def distance_3d(x1: float, y1: float, z1: float,
                x2: float, y2: float, z2: float) -> float:
    """3D расстояние между двумя точками."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def point_to_segment_distance(px: float, py: float,
                               x1: float, y1: float,
                               x2: float, y2: float) -> float:
    """
    Минимальное 2D расстояние от точки (px, py) до отрезка (x1,y1)-(x2,y2).
    Используется для линейных ИШ.
    """
    dx = x2 - x1
    dy = y2 - y1
    seg_len_sq = dx * dx + dy * dy

    if seg_len_sq < 1e-12:
        # Отрезок вырожден в точку
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

    t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))  # зажать в [0, 1]

    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)


def source_to_point_distance(src: "NoiseSource", pt: "CalcPoint") -> float:
    """
    Расстояние от ИШ до расчётной точки.
    Для точечного ИШ — 3D расстояние.
    Для линейного ИШ — минимальное расстояние от РТ до отрезка ИШ,
    с учётом разницы высот.
    """
    if src.source_type.value == "line" and src.x2 is not None and src.y2 is not None:
        r_2d = point_to_segment_distance(pt.x, pt.y, src.x, src.y, src.x2, src.y2)
        dz = pt.z - src.z
        return math.sqrt(r_2d ** 2 + dz ** 2)
    else:
        return distance_3d(src.x, src.y, src.z, pt.x, pt.y, pt.z)


def geometric_divergence_point(r: float, half_space: bool = True) -> float:
    """
    Геометрическое расхождение для точечного ИШ [дБ].
    Полупространство (у земли): 20·lg(r) + 8
    Свободное поле:              20·lg(r) + 11
    СП 51.13330.2011, п.7.3.
    """
    if r <= 0:
        raise ValueError(f"Расстояние должно быть > 0, получено {r}")
    correction = 8 if half_space else 11
    return 20 * math.log10(r) + correction


def geometric_divergence_line(r: float, half_space: bool = True) -> float:
    """
    Геометрическое расхождение для линейного ИШ [дБ].
    10·lg(r) + 8 (полупространство)
    СП 51.13330.2011, п.7.4.
    """
    if r <= 0:
        raise ValueError(f"Расстояние должно быть > 0, получено {r}")
    correction = 8 if half_space else 11
    return 10 * math.log10(r) + correction
