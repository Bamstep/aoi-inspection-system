

```markdown
# Edge Industrial Automated Optical Inspection (AOI) System

A low-latency, modular industrial machine vision microservice designed for automated dimensional metrology and surface defect detection on high-speed manufacturing lines.

Built with Python, OpenCV, and FastAPI, this system inspects cylindrical and machined components (such as bushings, bearings, and flanges), validates geometric tolerances against strict engineering thresholds, makes automated sorting decisions, and streams real-time visual telemetry to factory operators.

---

## Architecture Overview

```text
 ┌────────────────────────────────────────────────────────┐
 │   Calibrated Optical Ingestion (GigE / Mock Stream)    │
 │   - 1280x720 @ 25 FPS                                  │
 │   - Sub-millimeter drift & synthetic defect injection  │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │   Metrology Engine (src/core/metrology.py)             │
 │   - Otsu binarization & sub-pixel contour fitting      │
 │   - Outer Diameter (OD), Inner Diameter (ID)           │
 │   - Concentricity & runout error calculation           │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │   Surface Defect Module (src/core/detector.py)         │
 │   - Annular Region-of-Interest (ROI) masking           │
 │   - Laplacian gradient & edge anomaly scoring          │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │   Decision Engine & State Machine                      │
 │   - Verdict: PASS | REJECT_DIMENSION | REJECT_SURFACE  │
 │   - Routing: PACKAGING | REWORK | SCRAP                │
 └───────────────────────────┬────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
 ┌───────────────────────────┐ ┌──────────────────────────┐
 │ FastAPI Edge Streaming Hub│ │ SQLite Telemetry Sink    │
 │ - /video_feed (MJPEG HUD) │ │ - Per-part timestamps    │
 │ - /stats (Yield & OEE)    │ │ - Continuous audit trail │
 └───────────────────────────┘ └──────────────────────────┘

```

---

## Key Capabilities

* **High-Precision Metrology:** Evaluates Outer Diameter (OD), Inner Diameter (ID), and concentricity offset against configurable limits ($\pm 0.10\text{ mm}$) using sub-pixel contour fitting.
* **Surface Anomaly Detection:** Isolates the functional annular zone of components to flag scratches, burrs, and voids using localized gradient analysis.
* **Deterministic Routing Logic:** Evaluates incoming parts against `config/tolerances.yaml` to assign routing commands (`PASS`, `REJECT_DIMENSION`, `REJECT_SURFACE`, `SCRAP`).
* **Operator Visual HUD:** Overlays dynamic digital calipers, concentricity alignment crosshairs, and status banners directly onto the live feed.
* **Factory Telemetry & Quality Tracking:** Streams rolling yield metrics, part counts, and dimensional distributions via REST endpoints while maintaining an append-only audit trail in SQLite.
* **Containerized Edge Deployment:** Dockerized configuration ready for deployment on industrial IPCs and edge accelerators (e.g., NVIDIA Jetson).

---

## Project Structure

```text
aoi-inspection-system/
├── config/
│   └── tolerances.yaml          # Metrology boundaries and defect sensitivity
├── docker/
│   └── Dockerfile               # Edge container build specification
├── src/
│   ├── api/
│   │   └── app.py               # FastAPI video streaming and yield endpoints
│   ├── camera/
│   │   └── mock_stream.py       # Calibrated camera feed simulator
│   ├── core/
│   │   ├── detector.py          # Annular surface defect detection engine
│   │   └── metrology.py         # Sub-pixel dimensional measurement algorithms
│   └── pipeline/
│       ├── decision_engine.py   # Industrial routing state machine & HUD renderer
│       └── logger.py            # SQLite part transaction logger
├── tests/
│   └── test_metrology.py        # Automated Pytest suite for dimensional accuracy
├── main.py                      # Application bootstrap and server entrypoint
├── requirements.txt
└── README.md

```

---

## Quickstart

### 1. Prerequisites

* Python 3.10 or 3.11
* Virtual environment tool (`venv`)

### 2. Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/Bamstep/aoi-inspection-system.git](https://github.com/Bamstep/aoi-inspection-system.git)
cd aoi-inspection-system

# Create and activate virtual environment
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Run Unit Tests

Validate the metrology algorithms and tolerance boundary checks:

```bash
pytest tests/ -v

```

### 4. Start the Edge Inspection Node

```bash
python main.py

```

Open your browser and navigate to:

* **Live Inspection Dashboard:** `http://127.0.0.1:8000`
* **Real-Time Telemetry Stats:** `http://127.0.0.1:8000/stats`
* **Interactive API Docs:** `http://127.0.0.1:8000/docs`

---

## Configuration

Tolerances and physical scale factors are defined in `config/tolerances.yaml`:

```yaml
scale:
  pixels_per_mm: 10.0

metrology:
  target_outer_diameter_mm: 50.0
  target_inner_diameter_mm: 25.0
  tolerance_mm: 0.10
  max_concentricity_offset_mm: 0.08

defect_detection:
  laplacian_threshold: 45.0
  min_defect_area_px: 12

```

---

## Docker Deployment

To build and run the inspection container in an isolated edge runtime:

```bash
# Build the Docker image
docker build -t aoi-inspection-system -f docker/Dockerfile .

# Run the container
docker run -d -p 8000:8000 --name aoi_node aoi-inspection-system

```

---

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```

```
