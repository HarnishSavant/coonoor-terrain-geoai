"""
GeoAI Coonoor Project — FastAPI Backend & WebGIS Server
Serves:
- REST API endpoints for analytical datasets, statistics, and GeoJSON layers
- Static files for the interactive Leaflet WebGIS frontend
- PostGIS live database health and statistics query
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
WEB_APP_DIR = PROJECT_ROOT / "06_Outputs" / "Web_App"
TABLES_DIR = PROJECT_ROOT / "06_Outputs" / "Tables"
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"
OVERLAYS_META_PATH = PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "web_overlays_metadata.json"

app = FastAPI(
    title="Coonoor GeoAI Terrain Assessment API",
    description="Backend API and WebGIS service for Coonoor Taluk Terrain Trafficability & Visibility Assessment.",
    version="1.0.0"
)

# Enable CORS for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_json_file(p: Path) -> Dict[str, Any]:
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {p.name}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_csv_as_dicts(p: Path):
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {p.name}")
    import csv
    with open(p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

# ─── API Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/health")
def get_health():
    """Health check endpoint."""
    return {
        "status": "online",
        "project": "Coonoor GeoAI Terrain Trafficability & Visibility Assessment",
        "study_area": "Coonoor Taluk, The Nilgiris, Tamil Nadu, India",
        "crs": "EPSG:32643 (WGS 1984 UTM Zone 43N)",
        "dem_source": "Copernicus GLO-30 DSM",
        "landcover_source": "ESA WorldCover 2021 (10m)",
        "osm_source": "OpenStreetMap Highways"
    }

@app.get("/api/config")
def get_config():
    """Returns the project configuration."""
    return load_json_file(CONFIG_PATH)

@app.get("/api/metadata/overlays")
def get_overlays_metadata():
    """Returns bounding box and raster layer metadata for Leaflet overlays."""
    return load_json_file(OVERLAYS_META_PATH)

@app.get("/api/stats/terrain")
def get_terrain_stats():
    """Returns geomorphometric summary statistics (elevation, slope, aspect, TRI, hillshade)."""
    return load_csv_as_dicts(TABLES_DIR / "terrain_stats.csv")

@app.get("/api/stats/trafficability")
def get_trafficability_stats():
    """Returns MCE 4-class terrain trafficability metrics."""
    return load_csv_as_dicts(TABLES_DIR / "trafficability_class_summary.csv")

@app.get("/api/stats/visibility")
def get_visibility_stats():
    """Returns line-of-sight viewshed visibility analysis metrics."""
    return load_csv_as_dicts(TABLES_DIR / "visibility_summary.csv")

@app.get("/api/stats/landcover")
def get_landcover_stats():
    """Returns ESA WorldCover 2021 categorical distribution."""
    return load_csv_as_dicts(TABLES_DIR / "landcover_stats.csv")

@app.get("/api/stats/roads")
def get_road_stats():
    """Returns OpenStreetMap highway network statistics by classification."""
    return load_csv_as_dicts(TABLES_DIR / "road_network_stats.csv")

@app.get("/api/geojson/aoi")
def get_geojson_aoi():
    """Returns Coonoor Taluk AOI boundary as GeoJSON."""
    return load_json_file(WEB_APP_DIR / "data" / "coonoor_aoi.geojson")

@app.get("/api/geojson/roads")
def get_geojson_roads():
    """Returns OSM road network as GeoJSON."""
    return load_json_file(WEB_APP_DIR / "data" / "coonoor_roads.geojson")

@app.get("/api/geojson/observer")
def get_geojson_observer():
    """Returns vantage point observer location as GeoJSON."""
    return load_json_file(WEB_APP_DIR / "data" / "observer_point.geojson")

@app.get("/api/postgis/status")
def get_postgis_status():
    """Checks PostgreSQL / PostGIS database connection and returns table row counts."""
    import psycopg2
    ENV_PATH = PROJECT_ROOT / "09_Config" / ".env"
    env_vars = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    host = os.environ.get("PGHOST", env_vars.get("PGHOST", "localhost"))
    port = int(os.environ.get("PGPORT", env_vars.get("PGPORT", "5432")))
    database = os.environ.get("PGDATABASE", env_vars.get("PGDATABASE", "postgres"))
    user = os.environ.get("PGUSER", env_vars.get("PGUSER", "postgres"))
    password = os.environ.get("PGPASSWORD", env_vars.get("PGPASSWORD", "root"))
    schema_name = os.environ.get("PGSCHEMA", env_vars.get("PGSCHEMA", "coonoor_geoai"))

    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=database, user=user, password=password, connect_timeout=3
        )
        cur = conn.cursor()
        tables = ["aoi_boundary", "roads_network", "observer_points", "viewshed_zones", 
                  "trafficability_classes", "landcover_classes", "terrain_statistics"]
        counts = {}
        for tbl in tables:
            cur.execute(f"SELECT COUNT(*) FROM {schema_name}.{tbl};")
            counts[tbl] = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {
            "status": "connected",
            "host": host,
            "port": port,
            "database": database,
            "schema": schema_name,
            "table_counts": counts
        }
    except Exception as e:
        return {
            "status": "error",
            "error_detail": str(e)
        }

# ─── Static Files & WebGIS Frontend ──────────────────────────────────────────

# Mount static directories
app.mount("/overlays", StaticFiles(directory=str(WEB_APP_DIR / "overlays")), name="overlays")
app.mount("/data", StaticFiles(directory=str(WEB_APP_DIR / "data")), name="data")

@app.get("/")
def serve_index():
    """Serves the main WebGIS interactive application."""
    index_file = WEB_APP_DIR / "index.html"
    return FileResponse(index_file)

@app.get("/style.css")
def serve_css():
    return FileResponse(WEB_APP_DIR / "style.css", media_type="text/css")

@app.get("/app.js")
def serve_js():
    return FileResponse(WEB_APP_DIR / "app.js", media_type="application/javascript")

if __name__ == "__main__":
    port = 8000
    print(f"Starting Coonoor GeoAI Server at http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
