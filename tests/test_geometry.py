"""Unit тесты: геометрическое расхождение."""
import math
import pytest

from core.geometry import (
    geometric_divergence_point,
    geometric_divergence_line,
    distance_3d,
    point_to_segment_distance,
    source_to_point_distance,
)
from core.models import NoiseSource, CalcPoint


@pytest.mark.parametrize("r,half_space,expected", [
    (50,  True,  20 * math.log10(50)  + 8),
    (100, True,  20 * math.log10(100) + 8),
    (200, True,  20 * math.log10(200) + 8),
    (100, False, 20 * math.log10(100) + 11),
])
def test_geometric_divergence_point(r, half_space, expected):
    result = geometric_divergence_point(r, half_space=half_space)
    assert abs(result - expected) < 0.01


@pytest.mark.parametrize("r,half_space,expected", [
    (50,  True,  10 * math.log10(50)  + 8),
    (100, True,  10 * math.log10(100) + 8),
    (200, True,  10 * math.log10(200) + 8),
])
def test_geometric_divergence_line(r, half_space, expected):
    result = geometric_divergence_line(r, half_space=half_space)
    assert abs(result - expected) < 0.01


def test_geometric_divergence_zero_raises():
    with pytest.raises(ValueError):
        geometric_divergence_point(0)


def test_distance_3d():
    assert abs(distance_3d(0, 0, 0, 3, 4, 0) - 5.0) < 1e-9
    assert abs(distance_3d(0, 0, 0, 0, 0, 0) - 0.0) < 1e-9


def test_point_to_segment_midpoint():
    # Точка перпендикулярна середине отрезка (0,0)-(4,0)
    d = point_to_segment_distance(2, 3, 0, 0, 4, 0)
    assert abs(d - 3.0) < 1e-9


def test_point_to_segment_endpoint():
    # Точка ближе к концу отрезка
    d = point_to_segment_distance(5, 0, 0, 0, 4, 0)
    assert abs(d - 1.0) < 1e-9


def test_source_to_point_distance_point_source():
    src = NoiseSource(id="s1", lw_octave=[80]*8, x=0, y=0, z=1)
    pt = CalcPoint(id="p1", x=0, y=100, z=1.5)
    r = source_to_point_distance(src, pt)
    expected = math.sqrt(100**2 + 0.5**2)
    assert abs(r - expected) < 0.01


def test_source_to_point_distance_line_source():
    src = NoiseSource(id="s1", source_type="line", lw_octave=[80]*8,
                      x=0, y=0, z=1, x2=100, y2=0)
    pt = CalcPoint(id="p1", x=50, y=30, z=1)
    r = source_to_point_distance(src, pt)
    assert abs(r - 30.0) < 0.01
