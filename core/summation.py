"""
Логарифмическое суммирование, A-взвешивание, коррекция на время.
"""
from __future__ import annotations

import math

from .constants import A_WEIGHTS, OCTAVE_FREQS, PDU, PDU_MAX_OFFSET


def log_sum(levels: list[float]) -> float:
    """
    Логарифмическое суммирование уровней [дБ].
    L_сум = 10·lg(Σ 10^(L_i/10))
    Уровни -inf (источник выключен) корректно игнорируются.
    """
    positive = [l for l in levels if l > -200]
    if not positive:
        return -math.inf
    return 10 * math.log10(sum(10 ** (l / 10) for l in positive))


def to_dba(octave_levels: list[float]) -> float:
    """
    Перевод октавных уровней в уровень звука А [дБА].
    L_А = 10·lg(Σ 10^((L_i + ΔL_Ai)/10))
    octave_levels: 8 значений для частот 63, 125, 250, 500, 1000, 2000, 4000, 8000 Гц.
    """
    weighted = [
        octave_levels[i] + A_WEIGHTS[OCTAVE_FREQS[i]]
        for i in range(8)
    ]
    return log_sum(weighted)


def equiv_level_correction(l_moment: float,
                            duration_hours: float,
                            period: str) -> float:
    """
    Коррекция уровня непостоянного ИШ на время работы.
    L_экв = L + 10·lg(T_раб / T_период)
    period: "day" (16 ч) или "night" (8 ч).
    """
    t_period_hours = 16.0 if period == "day" else 8.0
    if duration_hours <= 0:
        return -math.inf
    if duration_hours >= t_period_hours:
        return l_moment
    correction = 10 * math.log10(duration_hours / t_period_hours)
    return l_moment + correction


def get_pdu(territory_type: str, period: str) -> float:
    """ПДУ эквивалентного уровня [дБА] по типу территории и периоду."""
    return float(PDU[territory_type][period])


def get_pdu_max(territory_type: str, period: str) -> float:
    """ПДУ максимального уровня [дБА]."""
    return get_pdu(territory_type, period) + PDU_MAX_OFFSET
