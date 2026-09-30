import cv2
import numpy as np
import time
import random
from typing import Generator, Tuple, Dict, Any

class MockIndustrialStream:
    """Simulates an industrial inspection camera feed with ground truth metadata."""
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.pixel_to_mm = 0.045  # 1 px = 0.045 mm

    def generate_part(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        frame = np.full((self.height, self.width, 3), 35, dtype=np.uint8)
        noise = np.random.normal(0, 3, (self.height, self.width, 3)).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        center_x = self.width // 2 + random.randint(-15, 15)
        center_y = self.height // 2 + random.randint(-15, 15)

        is_defective_dim = random.random() < 0.25
        has_scratch = random.random() < 0.30

        nom_outer_px = int(25.0 / self.pixel_to_mm)
        nom_inner_px = int(8.5 / self.pixel_to_mm)

        if is_defective_dim:
            delta = random.choice([-25, 25])  # Out of tolerance
            outer_r = (nom_outer_px // 2) + delta
        else:
            delta = random.randint(-2, 2)     # Within tolerance
            outer_r = (nom_outer_px // 2) + delta

        inner_r = nom_inner_px // 2 + random.randint(-1, 1)

        # Draw outer metal ring & center bored hole
        cv2.circle(frame, (center_x, center_y), outer_r, (190, 195, 200), -1)
        cv2.circle(frame, (center_x, center_y), inner_r, (35, 35, 35), -1)

        defects = []
        if has_scratch:
            sx1 = center_x + random.randint(-outer_r + 20, outer_r - 20)
            sy1 = center_y + random.randint(-outer_r + 20, outer_r - 20)
            sx2 = sx1 + random.randint(30, 80)
            sy2 = sy1 + random.randint(-30, 30)
            cv2.line(frame, (sx1, sy1), (sx2, sy2), (250, 250, 250), 2)
            defects.append({"type": "scratch", "bbox": [min(sx1, sx2), min(sy1, sy2), max(sx1, sx2), max(sy1, sy2)]})

        metadata = {
            "ground_truth_outer_dia_mm": (outer_r * 2) * self.pixel_to_mm,
            "ground_truth_inner_dia_mm": (inner_r * 2) * self.pixel_to_mm,
            "has_defects": has_scratch,
            "defects": defects,
        }
        return frame, metadata

    def stream(self) -> Generator[Tuple[np.ndarray, Dict[str, Any]], None, None]:
        while True:
            start_time = time.time()
            frame, meta = self.generate_part()
            yield frame, meta
            elapsed = time.time() - start_time
            if elapsed < self.frame_delay:
                time.sleep(self.frame_delay - elapsed)
