"""Unit тесты: затухание звука."""
import math
import pytest

from core.attenuation import air_attenuation, screen_diffraction, calc_path_difference
from core.constants import AIR_ATTENUATION_DEFAULT


def test_air_attenuation_default_conditions():
    """При T=20°C φ=70% результат совпадает с таблицей ГОСТ."""
    for freq, alpha_km in AIR_ATTENUATION_DEFAULT.items():
        expected = alpha_km * 500 / 1000  # 500 м
        result = air_attenuation(freq, 500.0, temperature=20.0, humidity=70.0)
        assert abs(result - expected) < 0.001, f"freq={freq}: {result} != {expected}"


def test_air_attenuation_proportional_to_distance():
    """Затухание пропорционально расстоянию."""
    r1 = air_attenuation(1000, 100.0)
    r2 = air_attenuation(1000, 200.0)
    assert abs(r2 - 2 * r1) < 0.001


def test_screen_diffraction_zero_when_no_obstacle():
    """Нулевое значение при δ ≤ 0."""
    assert screen_diffraction(1000, 0.0) == 0.0
    assert screen_diffraction(1000, -1.0) == 0.0


def test_screen_diffraction_increases_with_delta():
    """Бо́льшая разность путей → большее снижение."""
    d1 = screen_diffraction(1000, 0.1)
    d2 = screen_diffraction(1000, 1.0)
    d3 = screen_diffraction(1000, 5.0)
    assert d1 < d2 < d3


def test_screen_diffraction_max_25db():
    """Максимальное снижение ограничено 25 дБ."""
    result = screen_diffraction(8000, 100.0)
    assert result <= 25.0


@pytest.mark.parametrize("freq,delta,expected_range", [
    (1000, 0.5, (5, 25)),  # умеренное снижение (N=2*0.5/0.34≈2.9, ΔL≈18 дБ)
    (4000, 1.0, (10, 25)),  # значительное снижение
])
def test_screen_diffraction_range(freq, delta, expected_range):
    result = screen_diffraction(freq, delta)
    assert expected_range[0] <= result <= expected_range[1]


def test_calc_path_difference_no_screen_between():
    """Экран вне зоны ИШ-РТ → δ = 0."""
    # ИШ в (0,0), РТ в (100,0), экран в (-10,0)-(−10,10)
    delta = calc_path_difference(0, 0, 1, 100, 0, 1.5,
                                  -10, 0, -10, 10, 3.0)
    assert delta == 0.0


def test_calc_path_difference_screen_between_positive():
    """Экран между ИШ и РТ → δ > 0."""
    # ИШ в (0,0), РТ в (100,0), экран в (50,−5)-(50,5) высота 5м
    delta = calc_path_difference(0, 0, 1, 100, 0, 1.5,
                                  50, -5, 50, 5, 5.0)
    assert delta > 0
