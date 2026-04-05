"""Unit тесты: логарифмическое суммирование и A-взвешивание."""
import math
import pytest

from core.summation import log_sum, to_dba, equiv_level_correction, get_pdu
from core.constants import A_WEIGHTS, OCTAVE_FREQS


def test_two_equal_sources_add_3db():
    """Два одинаковых источника = L + 3 дБ."""
    l = 60.0
    result = log_sum([l, l])
    assert abs(result - (l + 3.010)) < 0.01


def test_single_source_unchanged():
    """Один источник — уровень не изменяется."""
    assert abs(log_sum([75.0]) - 75.0) < 0.001


def test_ten_equal_sources_add_10db():
    """10 одинаковых источников = L + 10 дБ."""
    l = 50.0
    result = log_sum([l] * 10)
    assert abs(result - (l + 10.0)) < 0.01


def test_log_sum_empty():
    """Пустой список → -inf."""
    assert log_sum([]) == -math.inf


def test_a_weighting_1khz_unchanged():
    """На 1000 Гц поправка A = 0 дБ."""
    octave = [-200.0] * 8
    octave[4] = 60.0  # индекс 4 → 1000 Гц
    result = to_dba(octave)
    assert abs(result - 60.0) < 0.1


def test_a_weighting_all_freqs():
    """to_dba применяет A_WEIGHTS корректно для каждой частоты."""
    for idx, freq in enumerate(OCTAVE_FREQS):
        octave = [-200.0] * 8
        octave[idx] = 70.0
        result = to_dba(octave)
        expected = 70.0 + A_WEIGHTS[freq]
        assert abs(result - expected) < 0.1, f"freq={freq}"


def test_equiv_level_correction_permanent():
    """Постоянный ИШ (is_permanent=True) — коррекция не применяется к уровню."""
    l = 65.0
    # Если работает весь период (8ч = 8ч ночного периода)
    result = equiv_level_correction(l, 8.0, "night")
    assert abs(result - l) < 0.01


def test_equiv_level_correction_half_period():
    """Работает половину периода → коррекция -3 дБ."""
    l = 65.0
    # Ночь 8ч, работает 4ч → correction = 10·lg(4/8) = -3.01 дБ
    result = equiv_level_correction(l, 4.0, "night")
    assert abs(result - (l - 3.010)) < 0.01


def test_equiv_level_correction_zero_duration():
    """Нулевое время работы → -inf."""
    result = equiv_level_correction(65.0, 0.0, "day")
    assert result == -math.inf


def test_get_pdu_residential():
    assert get_pdu("residential", "day") == 55
    assert get_pdu("residential", "night") == 45


def test_get_pdu_industrial():
    assert get_pdu("industrial", "day") == 80
    assert get_pdu("industrial", "night") == 80
