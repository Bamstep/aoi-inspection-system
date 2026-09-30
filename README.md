Here is the complete, comprehensive `README.md` incorporating all the installation nuances, PowerShell execution policies, module execution for pytest, and full architecture details:

```markdown
# Edge Industrial Automated Optical Inspection (AOI) System

A low-latency, modular industrial machine vision microservice engineered for real-time dimensional metrology, surface defect segmentation, and automated routing on high-speed factory assembly lines.

Built with Python, OpenCV, and FastAPI, this system inspects cylindrical and machined components (such as bushings, bearings, and flanges), validates geometric tolerances against strict engineering thresholds, executes deterministic sorting states, and serves an operator heads-up display (HUD) alongside a live factory analytics stream.

---

## Architecture & Data Flow

```text
 ┌────────────────────────────────────────────────────────┐
 │   Calibrated Optical Ingestion (GigE / Mock Stream)    │
 │   - Resolution: 1280x720 @ 25 FPS                      │
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

* **High-Precision Metrology:** Evaluates Outer Diameter (OD), Inner Diameter (ID), and concentricity offset against strict tolerances ($\pm 0.10\text{ mm}$) using sub-pixel contour detection.
* **Surface Anomaly Detection:** Isolates the functional annular zone of components to flag scratches, burrs, and voids using localized gradient analysis.
* **Deterministic Routing Logic:** Evaluates incoming parts against `config/tolerances.yaml` to assign routing commands (`PASS`, `REJECT_DIMENSION`, `REJECT_SURFACE`, `SCRAP`).
* **Operator Visual HUD:** Overlays dynamic digital calipers, concentricity crosshairs, and status banners directly onto the live inspection feed.
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

## Quickstart Guide

### 1. Prerequisites

* Python 3.10, 3.11, or 3.13
* Git

---

### 2. Installation & Environment Setup

#### Clone the Repository

```bash
git clone [https://github.com/Bamstep/aoi-inspection-system.git](https://github.com/Bamstep/aoi-inspection-system.git)
cd aoi-inspection-system

```

#### Set Up Virtual Environment

**On Windows (PowerShell):**

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

```

**On Windows (Command Prompt):**

```cmd
python -m venv venv
.\venv\Scripts\activate.bat

```

**On Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate

```

#### Install Dependencies

```bash
pip install -r requirements.txt

```

---

### 3. Run Unit Tests

Execute tests using Python's module flag (`-m`) to guarantee the root directory is placed on Python's module search path:

```bash
python -m pytest tests/ -v

```

---

### 4. Launch the Edge Inspection Server

Start the application daemon:

```bash
python main.py

```

Once running, access the system via browser:

* **Live Inspection Dashboard & HUD:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Real-time Telemetry & Yield Stats:** [http://127.0.0.1:8000/stats](https://www.google.com/search?q=http://127.0.0.1:8000/stats)
* **Interactive OpenAPI Specs:** [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)

To shut down the service, press `Ctrl + C` in your terminal.

---

## Configuration

All physical scale factors and quality control thresholds are configured in `config/tolerances.yaml`:

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

## Troubleshooting

| Issue | Cause | Resolution |
| --- | --- | --- |
| `PSSecurityException: running scripts is disabled` | Windows PowerShell default execution policy | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before calling `.\venv\Scripts\Activate.ps1`. |
| `ModuleNotFoundError: No module named 'src'` | `pytest` run without root directory on `sys.path` | Run tests as a module: `python -m pytest tests/ -v`. |
| `port 8000 already in use` | A previous instance of the server is still running | Terminate the existing process or run Uvicorn on another port with `uvicorn src.api.app:app --port 8001`. |

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
