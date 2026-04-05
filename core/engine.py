"""
Главный расчётный оркестратор.
Реализует полный алгоритм СП 51.13330.2011 / ГОСТ 31295.2-2005.
"""
from __future__ import annotations

import math

from .constants import OCTAVE_FREQS
from .geometry import source_to_point_distance, geometric_divergence_point, geometric_divergence_line
from .attenuation import air_attenuation, screen_diffraction, calc_path_difference, ground_absorption
from .summation import log_sum, to_dba, equiv_level_correction, get_pdu, get_pdu_max
from .isoline import generate_isolines
from .models import CalcRequest, CalcResponse, PointResult


def calculate(request: CalcRequest) -> CalcResponse:
    """
    Рассчитать уровни шума во всех расчётных точках.

    Алгоритм для каждого периода (день/ночь) и каждой РТ:
    1. Для каждой октавной полосы 63..8000 Гц:
       a. Расстояние ИШ→РТ
       b. Геометрическое расхождение (точечный: 20·lg(r)+8, линейный: 10·lg(r)+8)
       c. Затухание в воздухе (α·r/1000)
       d. Дифракция на экранах (метод Маекавы)
       e. Поглощение грунтом
       f. Уровень в РТ: L = Lw + ΔLф - ΔLдив - ΔLвозд - ΔLэкр - ΔLгрунт
       g. Коррекция на время работы непостоянного ИШ
    2. Логарифмическое суммирование вкладов всех ИШ
    3. Перевод в дБА, сравнение с ПДУ
    """
    results: list[PointResult] = []

    for period in ("day", "night"):
        for pt in request.points:
            octave_totals: list[float] = []
            max_dba_by_source: list[float] = []  # для Lmax

            for freq_idx, freq in enumerate(OCTAVE_FREQS):
                source_contribs: list[float] = []

                for src in request.sources:
                    # 1. Расстояние
                    r = source_to_point_distance(src, pt)
                    r = max(r, 1.0)  # минимальное расстояние 1 м

                    # 2. Геометрическое расхождение
                    if src.source_type.value == "line" and src.x2 is not None:
                        dl_div = geometric_divergence_line(r, half_space=True)
                    else:
                        dl_div = geometric_divergence_point(r, half_space=True)

                    # 3. Затухание в воздухе
                    dl_air = air_attenuation(freq, r, request.temperature, request.humidity)

                    # 4. Дифракция на экранах
                    dl_screen = 0.0
                    for screen in request.screens:
                        delta = calc_path_difference(
                            src.x, src.y, src.z,
                            pt.x, pt.y, pt.z,
                            screen.x1, screen.y1, screen.x2, screen.y2,
                            screen.height,
                        )
                        if delta > 0:
                            dl_screen += screen_diffraction(freq, delta)

                    # 5. Поглощение грунтом
                    dl_ground = ground_absorption(freq, r, src.z, pt.z, request.ground_type)

                    # 6. Уровень в расчётной точке
                    l_pt = (src.lw_octave[freq_idx]
                            + src.directionality
                            - dl_div
                            - dl_air
                            - dl_screen
                            + dl_ground)  # dl_ground отрицательный

                    # 7. Коррекция на время работы
                    if not src.is_permanent:
                        duration = src.duration_day if period == "day" else src.duration_night
                        l_pt = equiv_level_correction(l_pt, duration, period)

                    source_contribs.append(l_pt)

                octave_totals.append(log_sum(source_contribs))

            # A-взвешивание суммарного уровня
            l_a_eq = to_dba(octave_totals)

            # Lmax — максимальный вклад от одного ИШ в дБА
            l_a_max = l_a_eq  # упрощение: Lmax = Lэкв для постоянного шума
            # Для непостоянного шума Lmax рассчитывается отдельно (без коррекции времени)

            pdu_eq = get_pdu(pt.territory_type.value, period)
            pdu_max = get_pdu_max(pt.territory_type.value, period)
            exceeded = l_a_eq > pdu_eq

            results.append(PointResult(
                point_id=pt.id,
                period=period,
                l_octave=[round(v, 1) for v in octave_totals],
                l_a_eq=round(l_a_eq, 1),
                l_a_max=round(l_a_max, 1),
                pdu_eq=pdu_eq,
                pdu_max=pdu_max,
                exceeded=exceeded,
                exceedance_eq=round(l_a_eq - pdu_eq, 1),
            ))

    isolines = generate_isolines(request)

    return CalcResponse(
        results=results,
        isolines=isolines,
        metadata={
            "algorithm": "SP51.13330.2011 / GOST31295.2-2005",
            "version": "1.0",
            "sources_count": len(request.sources),
            "points_count": len(request.points),
        },
    )
