import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class InspectionLogger:
    def __init__(self, db_path: str = "data/output_logs/telemetry.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inspection_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    action TEXT NOT NULL,
                    outer_diameter_mm REAL,
                    inner_diameter_mm REAL,
                    concentricity_mm REAL,
                    defect_count INTEGER
                )
            """)
            conn.commit()

    def log(self, result: Dict[str, Any]):
        metro = result.get("metrology")
        defects = result.get("defects", [])
        
        od = metro.outer_diameter_mm if metro else None
        id_dim = metro.inner_diameter_mm if metro else None
        conc = metro.concentricity_offset_mm if metro else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inspection_records 
                (timestamp, verdict, action, outer_diameter_mm, inner_diameter_mm, concentricity_mm, defect_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                result.get("verdict", "UNKNOWN"),
                result.get("action", "UNKNOWN"),
                od,
                id_dim,
                conc,
                len(defects)
            ))
            conn.commit()
