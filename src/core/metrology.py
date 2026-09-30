import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

@dataclass
class MetrologyResult:
    outer_diameter_mm: float
    inner_diameter_mm: float
    concentricity_offset_mm: float
    center_outer: Tuple[float, float]
    center_inner: Tuple[float, float]
    passed_tolerance: bool
    status_details: Dict[str, str]

class MetrologyEngine:
    def __init__(self, pixel_to_mm: float = 0.045, config: Optional[Dict[str, Any]] = None):
        self.pixel_to_mm = float(pixel_to_mm)
        self.cfg = config or {
            "outer_nom": 25.0, "outer_tol": 0.15,
            "inner_nom": 8.5,  "inner_tol": 0.10,
            "concentricity_max": 0.20
        }

    def inspect(self, frame: np.ndarray) -> Optional[MetrologyResult]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        if not contours or hierarchy is None:
            return None

        sorted_indices = sorted(range(len(contours)), key=lambda i: cv2.contourArea(contours[i]), reverse=True)
        if len(sorted_indices) < 2:
            return None

        outer_c = contours[sorted_indices[0]]
        inner_c = contours[sorted_indices[1]]

        (ox, oy), outer_radius = cv2.minEnclosingCircle(outer_c)
        (ix, iy), inner_radius = cv2.minEnclosingCircle(inner_c)

        outer_dia_mm = float((outer_radius * 2) * self.pixel_to_mm)
        inner_dia_mm = float((inner_radius * 2) * self.pixel_to_mm)

        dist_px = float(np.sqrt((ox - ix) ** 2 + (oy - iy) ** 2))
        concentricity_mm = float(dist_px * self.pixel_to_mm)

        outer_pass = bool(abs(outer_dia_mm - self.cfg["outer_nom"]) <= self.cfg["outer_tol"])
        inner_pass = bool(abs(inner_dia_mm - self.cfg["inner_nom"]) <= self.cfg["inner_tol"])
        conc_pass = bool(concentricity_mm <= self.cfg["concentricity_max"])

        return MetrologyResult(
            outer_diameter_mm=round(outer_dia_mm, 3),
            inner_diameter_mm=round(inner_dia_mm, 3),
            concentricity_offset_mm=round(concentricity_mm, 3),
            center_outer=(round(float(ox), 1), round(float(oy), 1)),
            center_inner=(round(float(ix), 1), round(float(iy), 1)),
            passed_tolerance=bool(outer_pass and inner_pass and conc_pass),
            status_details={
                "outer_diameter": "PASS" if outer_pass else f"FAIL ({outer_dia_mm:.2f}mm)",
                "inner_diameter": "PASS" if inner_pass else f"FAIL ({inner_dia_mm:.2f}mm)",
                "concentricity": "PASS" if conc_pass else f"FAIL ({concentricity_mm:.2f}mm)"
            }
        )
