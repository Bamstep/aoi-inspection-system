import pytest
import numpy as np
import cv2
from src.core.metrology import MetrologyEngine, MetrologyResult

@pytest.fixture
def metrology_engine():
    config = {
        "outer_nom": 20.0, "outer_tol": 0.20,
        "inner_nom": 8.0,  "inner_tol": 0.15,
        "concentricity_max": 0.15
    }
    return MetrologyEngine(pixel_to_mm=0.05, config=config)

def test_nominal_part_passes(metrology_engine):
    canvas = np.full((600, 600, 3), 30, dtype=np.uint8)
    center = (300, 300)
    cv2.circle(canvas, center, 200, (200, 200, 200), -1)
    cv2.circle(canvas, center, 80, (30, 30, 30), -1)

    result = metrology_engine.inspect(canvas)
    assert result is not None
    assert isinstance(result, MetrologyResult)
    assert result.passed_tolerance is True
    assert result.status_details["outer_diameter"] == "PASS"
    assert result.status_details["inner_diameter"] == "PASS"
    assert result.concentricity_offset_mm <= 0.15

def test_out_of_tolerance_outer_fails(metrology_engine):
    canvas = np.full((600, 600, 3), 30, dtype=np.uint8)
    center = (300, 300)
    cv2.circle(canvas, center, 220, (200, 200, 200), -1)
    cv2.circle(canvas, center, 80, (30, 30, 30), -1)

    result = metrology_engine.inspect(canvas)
    assert result is not None
    assert result.passed_tolerance is False
    assert "FAIL" in result.status_details["outer_diameter"]
