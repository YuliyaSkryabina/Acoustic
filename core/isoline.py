"""
Генерация изолиний уровня звука через matplotlib.contour.
Возвращает список IsolineFeature для отображения на карте.
"""
from __future__ import annotations

import math
import warnings
from typing import TYPE_CHECKING

import numpy as np

from .constants import OCTAVE_FREQS, A_WEIGHTS, AIR_ATTENUATION_DEFAULT
from .models import IsolineFeature

if TYPE_CHECKING:
    from .models import CalcRequest


def _quick_dba_at_point(sources, px: float, py: float, pz: float = 1.5) -> float:
    """
    Быстрый расчёт уровня дБА в точке сетки (упрощённый, без экранов).
    Используется только для построения изолиний.
    """
    total_per_freq = []
    for freq_idx, freq in enumerate(OCTAVE_FREQS):
        contribs = []
        for src in sources:
            r = math.sqrt((px - src.x) ** 2 + (py - src.y) ** 2 + (pz - src.z) ** 2)
            if r < 1.0:
                r = 1.0
            div = 20 * math.log10(r) + 8  # точечный ИШ, полупространство
            air = AIR_ATTENUATION_DEFAULT[freq] * r / 1000.0
            l = src.lw_octave[freq_idx] + src.directionality - div - air
            contribs.append(l)
        # Суммирование
        total_per_freq.append(10 * math.log10(sum(10 ** (l / 10) for l in contribs)) if contribs else -200)

    # A-взвешивание
    weighted = [total_per_freq[i] + A_WEIGHTS[OCTAVE_FREQS[i]] for i in range(8)]
    return 10 * math.log10(sum(10 ** (w / 10) for w in weighted if w > -200))


def generate_isolines(request: "CalcRequest",
                      grid_step: float = 10.0,
                      levels_dba: list[float] | None = None) -> list[IsolineFeature]:
    """
    Построить сетку уровней звука и извлечь изолинии.
    Возвращает список IsolineFeature (GeoJSON-подобные объекты).
    """
    if not request.sources:
        return []

    if levels_dba is None:
        levels_dba = list(range(25, 90, 5))

    # Определить bbox
    all_x = [s.x for s in request.sources]
    all_y = [s.y for s in request.sources]
    margin = max(100.0, grid_step * 10)
    x_min, x_max = min(all_x) - margin, max(all_x) + margin
    y_min, y_max = min(all_y) - margin, max(all_y) + margin

    x_range = np.arange(x_min, x_max + grid_step, grid_step)
    y_range = np.arange(y_min, y_max + grid_step, grid_step)

    if len(x_range) < 4 or len(y_range) < 4:
        return []

    X, Y = np.meshgrid(x_range, y_range)
    Z = np.zeros_like(X)

    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i, j] = _quick_dba_at_point(request.sources, X[i, j], Y[i, j])

    # Извлечь изолинии через matplotlib
    try:
        import matplotlib
        matplotlib.use("Agg")  # без GUI
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cs = ax.contour(X, Y, Z, levels=levels_dba)

        features: list[IsolineFeature] = []
        for level, collection in zip(cs.levels, cs.collections):
            for path in collection.get_paths():
                coords = path.vertices.tolist()
                if len(coords) >= 2:
                    features.append(IsolineFeature(
                        level_dba=float(level),
                        coordinates=coords,
                    ))
        plt.close(fig)
        return features
    except Exception:
        return []
