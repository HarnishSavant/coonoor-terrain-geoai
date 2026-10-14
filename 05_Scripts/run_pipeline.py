"""
Master Pipeline Runner: Coonoor GeoAI Project
Executes all modular workflow stages sequentially:
  00. Inspect Environment & Verify ArcPy / PostgreSQL
  01. Validate AOI Geometry & Bounds
  02. Acquire & Process Copernicus GLO-30 DEM
  03. Generate Geomorphometric Surface Derivatives
  04. Acquire & Process OpenStreetMap Road Network
  05. Build Multi-Criteria Trafficability & Accessibility Index
  06. Compute Topographic Viewshed & Visibility Demonstration
  08. Load Spatial Vector & Tabular Datasets into PostGIS
  09. Generate Cartographic Maps & Analytical Figures
  10. Execute Machine Learning Feature Extraction & Surrogate Training
  07. Perform Quality Audit & Deliverable Manifest Validation
"""
import sys
import os
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
SCRIPTS_DIR = PROJECT_ROOT / "05_Scripts"
ML_DIR = PROJECT_ROOT / "11_ML"
LOGS_DIR = PROJECT_ROOT / "08_Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

pipeline_log_path = LOGS_DIR / "pipeline_execution.log"

stages = [
    ("Stage 00: Environment & ArcPy Inspection", SCRIPTS_DIR / "00_inspect_environment.py"),
    ("Stage 01: AOI Geometry & Boundary Validation", SCRIPTS_DIR / "01_validate_aoi.py"),
    ("Stage 02: Copernicus GLO-30 DEM Acquisition", SCRIPTS_DIR / "02_acquire_dem.py"),
    ("Stage 03: Geomorphometric Derivatives (ArcPy)", SCRIPTS_DIR / "03_process_terrain.py"),
    ("Stage 03b: ESA WorldCover 2021 Land Cover Processing", SCRIPTS_DIR / "03b_process_worldcover.py"),
    ("Stage 04: OSM Transport Network & Proximity", SCRIPTS_DIR / "04_acquire_osm.py"),
    ("Stage 05: Multi-Criteria Trafficability Index", SCRIPTS_DIR / "05_build_accessibility_index.py"),
    ("Stage 06: Line-of-Sight Viewshed Demonstration", SCRIPTS_DIR / "06_visibility_analysis.py"),
    ("Stage 08: PostgreSQL/PostGIS Database Loading", SCRIPTS_DIR / "08_load_postgis.py"),
    ("Stage 09: Cartographic Maps & Analytical Figures", SCRIPTS_DIR / "09_create_maps_and_report.py"),
    ("Stage 10a: Machine Learning Surrogate Modeling", ML_DIR / "train_surrogate_model.py"),
    ("Stage 10b: Leaflet Web Overlays Generation", SCRIPTS_DIR / "10_generate_web_overlays.py"),
    ("Stage 10c: WGS84 GeoJSON Vectors Export", SCRIPTS_DIR / "11_export_web_geojson.py"),
    ("Stage 07: Data Quality Audit & Deliverable Manifest", SCRIPTS_DIR / "07_validate_outputs.py")
]

print("=" * 70)
print("COONOOR GEOAI AUTOMATED WORKFLOW PIPELINE")
print("Target: Coonoor Taluk, The Nilgiris, Tamil Nadu, India")
print("CRS: WGS 1984 UTM Zone 43N (EPSG:32643)")
print("Python Executable:", sys.executable)
print("=" * 70)

log_entries = [
    "=" * 70,
    "COONOOR GEOAI PIPELINE EXECUTION SUMMARY",
    f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    "=" * 70
]

pipeline_start = time.time()
all_passed = True

for title, script_path in stages:
    print(f"\n>>> Running: {title}")
    t0 = time.time()
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    duration = time.time() - t0
    
    if result.returncode == 0:
        status_str = "SUCCESS"
        print(f"    Status: SUCCESS ({duration:.1f}s)")
        log_entries.append(f"{title:<52} : SUCCESS ({duration:5.1f}s)")
    else:
        status_str = "FAILED"
        all_passed = False
        print(f"    Status: FAILED (Exit Code: {result.returncode}, {duration:.1f}s)")
        print(f"    Stderr:\n{result.stderr.strip()[:400]}")
        log_entries.append(f"{title:<52} : FAILED  ({duration:5.1f}s, Code {result.returncode})")

total_duration = time.time() - pipeline_start
log_entries.append("=" * 70)
log_entries.append(f"TOTAL PIPELINE DURATION: {total_duration:.1f} seconds")
log_entries.append(f"OVERALL STATUS: {'ALL STAGES PASSED (100%)' if all_passed else 'SOME STAGES FAILED'}")
log_entries.append("=" * 70)

with open(pipeline_log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_entries))

print("\n" + "\n".join(log_entries))
print(f"\nPipeline log saved to: {pipeline_log_path}")
