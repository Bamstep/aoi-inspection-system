import cv2
import numpy as np
from typing import List, Dict, Any

class DefectDetector:
    def __init__(self, onnx_model_path: str = None, conf_threshold: float = 0.5):
        self.conf_threshold = conf_threshold
        self.session = None
        if onnx_model_path:
            import onnxruntime as ort
            self.session = ort.InferenceSession(onnx_model_path)

    def detect(self, frame: np.ndarray, part_mask_center: tuple, outer_radius: int) -> List[Dict[str, Any]]:
        findings = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        mask = np.zeros_like(gray)
        cx, cy = int(part_mask_center[0]), int(part_mask_center[1])
        cv2.circle(mask, (cx, cy), int(outer_radius * 0.95), 255, -1)
        cv2.circle(mask, (cx, cy), int(outer_radius * 0.40), 0, -1)

        laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
        laplacian = np.uint8(np.absolute(laplacian))
        anomalies = cv2.bitwise_and(laplacian, laplacian, mask=mask)

        _, defect_thresh = cv2.threshold(anomalies, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(defect_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area > 15:
                x, y, w, h = cv2.boundingRect(c)
                findings.append({
                    "class": "scratch/burr",
                    "confidence": min(0.99, round(0.65 + (area / 100.0) * 0.2, 2)),
                    "bbox": [x, y, x + w, y + h]
                })

        return findings
