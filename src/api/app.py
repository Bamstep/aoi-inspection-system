from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import sqlite3
from src.camera.mock_stream import MockIndustrialStream
from src.core.metrology import MetrologyEngine
from src.core.detector import DefectDetector
from src.pipeline.decision_engine import DecisionEngine
from src.pipeline.logger import InspectionLogger

app = FastAPI(title="Edge AOI System Streamer")

camera = MockIndustrialStream(width=1280, height=720, fps=25)
metrology = MetrologyEngine(pixel_to_mm=camera.pixel_to_mm)
detector = DefectDetector()
logger = InspectionLogger()

def generate_frames():
    for raw_frame, _ in camera.stream():
        metro_res = metrology.inspect(raw_frame)
        defects = []
        if metro_res:
            r_px = int(metro_res.outer_diameter_mm / (2 * camera.pixel_to_mm))
            defects = detector.detect(raw_frame, metro_res.center_outer, r_px)

        decision = DecisionEngine.evaluate(metro_res, defects)
        hud_frame = DecisionEngine.draw_hud(raw_frame, decision)
        
        # Asynchronously log telemetry
        logger.log(decision)

        _, buffer = cv2.imencode('.jpg', hud_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
def get_stats():
    with sqlite3.connect("data/output_logs/telemetry.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inspection_records")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM inspection_records WHERE verdict = 'PASS'")
        passed = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(outer_diameter_mm), AVG(inner_diameter_mm) FROM inspection_records")
        avg_od, avg_id = cursor.fetchone()

    yield_rate = (passed / total * 100) if total > 0 else 0
    return {
        "total_parts_inspected": total,
        "parts_passed": passed,
        "yield_rate_percent": round(yield_rate, 2),
        "avg_outer_diameter_mm": round(avg_od, 3) if avg_od else 0,
        "avg_inner_diameter_mm": round(avg_id, 3) if avg_id else 0
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Edge AOI Live Console</title>
            <style>
                body { background: #111; color: #eee; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
                .container { display: flex; flex-direction: column; align-items: center; }
                .stream-box { border: 2px solid #444; border-radius: 8px; width: 80%; max-width: 960px; }
                .stats-panel { margin-top: 15px; font-size: 1.1em; color: #39ff14; }
            </style>
        </head>
        <body>
            <h2>Industrial AOI Edge Inspection Console</h2>
            <div class="container">
                <img src="/video_feed" class="stream-box" />
                <div class="stats-panel" id="metrics">Loading telemetry...</div>
            </div>
            <script>
                async function fetchStats() {
                    try {
                        const res = await fetch('/stats');
                        const data = await res.json();
                        document.getElementById('metrics').innerText = 
                            `Total Inspected: ${data.total_parts_inspected} | Passed: ${data.parts_passed} | Yield Rate: ${data.yield_rate_percent}%`;
                    } catch (e) {}
                }
                setInterval(fetchStats, 1000);
            </script>
        </body>
    </html>
    """
