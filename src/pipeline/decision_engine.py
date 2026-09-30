import cv2
import numpy as np
from typing import Dict, Any, List
from src.core.metrology import MetrologyResult

class DecisionEngine:
    @staticmethod
    def evaluate(metrology: MetrologyResult, defects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not metrology:
            return {"verdict": "NO_PART_DETECTED", "action": "HALT"}

        dim_pass = metrology.passed_tolerance
        surface_pass = len(defects) == 0

        if dim_pass and surface_pass:
            verdict = "PASS"
            action = "ROUTE_TO_PACKAGING"
        elif not dim_pass and surface_pass:
            verdict = "REJECT_DIMENSION"
            action = "ROUTE_TO_REWORK_OR_SCRAP"
        elif dim_pass and not surface_pass:
            verdict = "REJECT_SURFACE"
            action = "ROUTE_TO_DEBURR_POLISH"
        else:
            verdict = "REJECT_MULTIPLE_FAILS"
            action = "SCRAP"

        return {
            "verdict": verdict,
            "action": action,
            "metrology": metrology,
            "defects": defects
        }

    @staticmethod
    def draw_hud(frame: np.ndarray, result: Dict[str, Any]) -> np.ndarray:
        hud = frame.copy()
        verdict = result.get("verdict", "UNKNOWN")
        color = (0, 220, 0) if verdict == "PASS" else (0, 0, 235)

        # Top Header Bar
        cv2.rectangle(hud, (0, 0), (hud.shape[1], 65), (20, 20, 20), -1)
        cv2.putText(hud, f"STATUS: {verdict}", (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        cv2.putText(hud, f"ACTION: {result.get('action')}", (620, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (210, 210, 210), 2)

        # Metrology Visual Overlays
        metro = result.get("metrology")
        if metro and isinstance(metro, MetrologyResult):
            ox, oy = int(metro.center_outer[0]), int(metro.center_outer[1])
            cv2.circle(hud, (ox, oy), int(metro.outer_diameter_mm / (2 * 0.045)), (0, 255, 255), 1)
            cv2.circle(hud, (ox, oy), int(metro.inner_diameter_mm / (2 * 0.045)), (0, 255, 255), 1)

            # Lower-left Telemetry Box
            cv2.rectangle(hud, (15, hud.shape[0] - 125), (420, hud.shape[0] - 15), (20, 20, 20), -1)
            cv2.putText(hud, f"OD: {metro.outer_diameter_mm:.2f}mm [{metro.status_details['outer_diameter']}]", 
                        (25, hud.shape[0] - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(hud, f"ID: {metro.inner_diameter_mm:.2f}mm [{metro.status_details['inner_diameter']}]", 
                        (25, hud.shape[0] - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(hud, f"Concentricity: {metro.concentricity_offset_mm:.3f}mm", 
                        (25, hud.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        # Defect Callouts
        for d in result.get("defects", []):
            x1, y1, x2, y2 = d["bbox"]
            cv2.rectangle(hud, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(hud, f"{d['class']} {d['confidence']*100:.0f}%", (x1, max(18, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return hud
