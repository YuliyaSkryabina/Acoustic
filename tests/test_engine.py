"""
Интеграционный тест расчётного ядра.
Проверка точности ±0.5 дБ от СП 51.13330.2011.
"""
import math
import pytest

from core.engine import calculate
from core.models import CalcRequest, NoiseSource, CalcPoint, Screen


# Тестовый сценарий: одиночный точечный ИШ, открытое пространство
# Lw = 100 дБ на всех октавах, расстояние 50 м, полупространство
# Теоретический расчёт (1000 Гц):
#   ΔLдив = 20·lg(50) + 8 = 34.0 + 8 = 42.0 дБ
#   ΔLвозд = 3.7 · 50/1000 = 0.185 дБ
#   L(1000Гц) = 100 - 42.0 - 0.185 ≈ 57.8 дБ
SINGLE_SOURCE_LW = 100.0
SINGLE_SOURCE_R = 50.0
SINGLE_SOURCE_FREQ = 1000  # Гц, индекс 4


def make_single_source_request() -> CalcRequest:
    lw = [SINGLE_SOURCE_LW] * 8
    return CalcRequest(
        sources=[NoiseSource(id="src1", lw_octave=lw, x=0, y=0, z=1.0)],
        points=[CalcPoint(id="pt1", x=SINGLE_SOURCE_R, y=0, z=1.5,
                          territory_type="industrial")],
        temperature=20.0,
        humidity=70.0,
    )


def test_single_source_octave_level_1khz():
    """1000 Гц: уровень в РТ = Lw - ΔLдив - ΔLвозд."""
    req = make_single_source_request()
    resp = calculate(req)

    day_result = next(r for r in resp.results if r.period == "day")
    freq_idx = 4  # 1000 Гц

    r = math.sqrt(SINGLE_SOURCE_R ** 2 + 0.5 ** 2)  # 3D с dz=0.5
    dl_div = 20 * math.log10(r) + 8
    dl_air = 3.7 * r / 1000
    expected = SINGLE_SOURCE_LW - dl_div - dl_air

    assert abs(day_result.l_octave[freq_idx] - expected) < 0.5, \
        f"L(1кГц)={day_result.l_octave[freq_idx]:.1f}, ожидалось≈{expected:.1f}"


def test_single_source_dba_level():
    """дБА уровень для Lw=100 дБ, r=50 м должен быть в разумном диапазоне."""
    req = make_single_source_request()
    resp = calculate(req)

    day_result = next(r for r in resp.results if r.period == "day")
    # Для Lw=100 на всех октавах, r=50 м ожидаемый диапазон ≈ 55-70 дБА
    assert 50 <= day_result.l_a_eq <= 75, \
        f"L_A_eq={day_result.l_a_eq} дБА вне ожидаемого диапазона"


def test_level_decreases_with_distance():
    """Уровень убывает с расстоянием."""
    def level_at(r: float) -> float:
        req = CalcRequest(
            sources=[NoiseSource(id="s", lw_octave=[80]*8, x=0, y=0, z=1)],
            points=[CalcPoint(id="p", x=r, y=0, z=1.5, territory_type="industrial")],
        )
        resp = calculate(req)
        return next(r for r in resp.results if r.period == "day").l_a_eq

    l50 = level_at(50)
    l100 = level_at(100)
    l200 = level_at(200)
    assert l50 > l100 > l200, "Уровень должен убывать с расстоянием"


def test_two_sources_higher_than_one():
    """Два источника дают больший уровень, чем один."""
    def calc(n_sources: int) -> float:
        sources = [NoiseSource(id=f"s{i}", lw_octave=[80]*8, x=i*0.1, y=0, z=1)
                   for i in range(n_sources)]
        req = CalcRequest(
            sources=sources,
            points=[CalcPoint(id="p", x=50, y=0, z=1.5, territory_type="industrial")],
        )
        resp = calculate(req)
        return next(r for r in resp.results if r.period == "day").l_a_eq

    assert calc(2) > calc(1)
    assert calc(4) > calc(2)


def test_results_have_day_and_night():
    """Результаты содержат оба периода для каждой РТ."""
    req = make_single_source_request()
    resp = calculate(req)

    point_ids = {r.point_id for r in resp.results}
    assert "pt1" in point_ids

    day_results = [r for r in resp.results if r.period == "day"]
    night_results = [r for r in resp.results if r.period == "night"]
    assert len(day_results) == 1
    assert len(night_results) == 1


def test_industrial_not_exceeded():
    """Слабый ИШ на промышленной территории — норма."""
    req = CalcRequest(
        sources=[NoiseSource(id="s", lw_octave=[60]*8, x=0, y=0, z=1)],
        points=[CalcPoint(id="p", x=200, y=0, z=1.5, territory_type="industrial")],
    )
    resp = calculate(req)
    day = next(r for r in resp.results if r.period == "day")
    # ПДУ промышленная = 80 дБА, слабый ИШ на большом расстоянии
    assert not day.exceeded or day.l_a_eq <= 80


def test_exceedance_sign():
    """exceedance_eq = l_a_eq - pdu_eq."""
    req = make_single_source_request()
    resp = calculate(req)
    for result in resp.results:
        expected_exc = round(result.l_a_eq - result.pdu_eq, 1)
        assert abs(result.exceedance_eq - expected_exc) < 0.2


def test_screen_reduces_level():
    """Экран между ИШ и РТ снижает уровень."""
    base_req = CalcRequest(
        sources=[NoiseSource(id="s", lw_octave=[90]*8, x=0, y=0, z=1)],
        points=[CalcPoint(id="p", x=80, y=0, z=1.5, territory_type="industrial")],
    )
    screened_req = CalcRequest(
        sources=base_req.sources,
        points=base_req.points,
        screens=[Screen(id="scr", x1=40, y1=-10, x2=40, y2=10, height=6.0)],
    )

    base_resp = calculate(base_req)
    screened_resp = calculate(screened_req)

    base_day = next(r for r in base_resp.results if r.period == "day")
    screened_day = next(r for r in screened_resp.results if r.period == "day")

    assert screened_day.l_a_eq <= base_day.l_a_eq, \
        f"Экран не снизил уровень: {screened_day.l_a_eq} > {base_day.l_a_eq}"
