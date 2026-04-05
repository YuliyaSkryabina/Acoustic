"""
Затухание звука: воздух, дифракция на экране, поглощение грунтом.
ГОСТ 31295.2-2005, разделы 7–9.
"""
from __future__ import annotations

import math

from .constants import AIR_ATTENUATION_DEFAULT, AIR_ATTENUATION_TABLE, SPEED_OF_SOUND


def _interpolate_air_coeff(freq: int, temperature: float, humidity: float) -> float:
    """
    Коэффициент затухания воздуха α [дБ/км] для заданных T и φ.
    Интерполирует по ближайшим точкам из таблицы ГОСТ 31295.2-2005.
    """
    # Найти ближайшие записи в таблице
    best_key = min(AIR_ATTENUATION_TABLE.keys(),
                   key=lambda k: abs(k[0] - temperature) + abs(k[1] - humidity) * 0.1)
    return AIR_ATTENUATION_TABLE[best_key][freq]


def air_attenuation(freq: int, distance_m: float,
                    temperature: float = 20.0,
                    humidity: float = 70.0) -> float:
    """
    Затухание звука в воздухе [дБ] на расстоянии distance_m.
    ГОСТ 31295.2-2005, раздел 5, Приложение B.
    """
    if abs(temperature - 20.0) < 1.0 and abs(humidity - 70.0) < 5.0:
        alpha = AIR_ATTENUATION_DEFAULT[freq]
    else:
        alpha = _interpolate_air_coeff(freq, temperature, humidity)
    return alpha * distance_m / 1000.0


def screen_diffraction(freq: int, delta_path: float) -> float:
    """
    Снижение шума экраном по методу Маекавы [дБ].
    ΔL_экр = 10·lg(3 + 20·N), где N = 2·δ/λ
    ГОСТ 31295.2-2005, раздел 9.

    delta_path: разность длин путей δ [м] (путь через верх экрана − прямой путь).
    Если δ ≤ 0 — экран не экранирует (прямая видимость сохраняется).
    """
    if delta_path <= 0:
        return 0.0
    wavelength = SPEED_OF_SOUND / freq
    N = 2 * delta_path / wavelength
    attenuation = 10 * math.log10(3 + 20 * N)
    return min(attenuation, 25.0)  # практический предел по ГОСТ


def calc_path_difference(src_x: float, src_y: float, src_z: float,
                          pt_x: float, pt_y: float, pt_z: float,
                          screen_x1: float, screen_y1: float,
                          screen_x2: float, screen_y2: float,
                          screen_height: float) -> float:
    """
    Геометрическая разность путей δ для дифракции на экране [м].
    Метод: 2D проекция в плоскость ИШ-экран-РТ.

    Возвращает δ > 0 если экран находится между ИШ и РТ (экранирование),
    δ ≤ 0 — прямая видимость.
    """
    # Середина экрана (верхний край)
    mx = (screen_x1 + screen_x2) / 2
    my = (screen_y1 + screen_y2) / 2
    mz = screen_height  # верх экрана

    # Проверить, находится ли середина экрана между ИШ и РТ в плане
    # (упрощённая 2D проверка — экран проецируется на прямую ИШ-РТ)
    dx_sp = pt_x - src_x
    dy_sp = pt_y - src_y
    len_sp_2d = math.sqrt(dx_sp ** 2 + dy_sp ** 2)

    if len_sp_2d < 1e-6:
        return 0.0

    # Проекция середины экрана на отрезок ИШ-РТ
    t = ((mx - src_x) * dx_sp + (my - src_y) * dy_sp) / (len_sp_2d ** 2)
    if t <= 0 or t >= 1:
        # Экран не между ИШ и РТ
        return 0.0

    # Расстояния: ИШ→вершина экрана и вершина экрана→РТ
    d_src_top = math.sqrt((mx - src_x) ** 2 + (my - src_y) ** 2 + (mz - src_z) ** 2)
    d_top_pt = math.sqrt((pt_x - mx) ** 2 + (pt_y - my) ** 2 + (pt_z - mz) ** 2)

    # Прямое расстояние ИШ→РТ
    d_direct = math.sqrt((pt_x - src_x) ** 2 + (pt_y - src_y) ** 2 + (pt_z - src_z) ** 2)

    delta = d_src_top + d_top_pt - d_direct
    return max(0.0, delta)


def ground_absorption(freq: int, distance_m: float,
                       src_z: float, pt_z: float,
                       ground_type: float = 0.0) -> float:
    """
    Поправка на поглощение поверхностью земли [дБ].
    ГОСТ 31295.2-2005, раздел 7.
    ground_type: G = 0 (твёрдая: асфальт, бетон) .. 1 (мягкая: трава, грунт).
    Возвращает отрицательное значение (снижение уровня).
    """
    if ground_type < 0.01 or distance_m < 1.0:
        return 0.0

    # Упрощённая формула для расстояний > 50 м
    if distance_m < 50:
        return 0.0

    # Средняя высота пути [м]
    h_mean = (src_z + pt_z) / 2.0

    # Поправка растёт с расстоянием и убывает с высотой
    # Приближение по СП 51 Приложение Д
    base = -4.8 - (2 * h_mean / distance_m) * (17 + 300 / distance_m)
    return max(base * ground_type, -15.0)
