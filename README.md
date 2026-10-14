# GeoAI-Based Terrain Trafficability & Visibility Assessment
### A Case Study of Coonoor Taluk, The Nilgiris, Tamil Nadu, India

[![ArcGIS Pro 3.5](https://img.shields.io/badge/ArcGIS%20Pro-3.5-brightgreen)](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview)
[![ArcPy](https://img.shields.io/badge/ArcPy-3.5%20(Spatial%20Analyst)-blue)](https://pro.arcgis.com/en/pro-app/latest/arcpy/main/arcgis-pro-arcpy.htm)
[![Python 3.11](https://img.shields.io/badge/Python-3.11.11-yellow)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)](https://fastapi.tiangolo.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-green)](https://leafletjs.com/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.6%20%2F%20PostgreSQL%2018-blueviolet)](https://postgis.net/)
[![Compliance Score](https://img.shields.io/badge/Deliverables-50%2F50%20(100%25)-success)](./08_Logs/data_quality_report.txt)

---

## Executive Overview
This repository delivers an end-to-end, reproducible GeoAI spatial analysis pipeline and interactive WebGIS platform evaluating physical terrain accessibility (trafficability), line-of-sight visibility, and land cover classification across **Coonoor Taluk (222.44 km²)** in the high-relief Nilgiris Western Ghats of Tamil Nadu, India.

Combining high-resolution satellite-derived Digital Elevation Models (**Copernicus GLO-30**), **ESA WorldCover 2021** (10m), OpenStreetMap transportation corridors, ArcPy Spatial Analyst surface geomorphometry, Multi-Criteria Evaluation (MCE), Enterprise PostGIS database storage, and a modern **FastAPI + Leaflet WebGIS application**, the pipeline automates the transformation of raw geographic data into interactive analytical layers, publication-ready cartographic maps, tabular summaries, and Machine Learning surrogate models.

---

## Key Project Deliverables & Verified Metrics

| Metric / Layer | Value / Extent | Verification Details |
| :--- | :--- | :--- |
| **Study Area Extent** | 222.44 km² (22,244.04 ha) | EPSG:32643 (UTM Zone 43N), 101-vertex boundary |
| **Elevation Range** | 413.07 m to 2,388.21 m | Mean: 1,635.93 m MSL, Copernicus GLO-30 (30m) |
| **Slope Gradient** | 0.03° to 75.78° (Mean: 20.58°) | 39.06 km² (17.7%) exceeds 30° critical movement barrier |
| **Terrain Ruggedness (TRI)** | 0.24 m to 303.73 m | 3x3 focal elevation range (Mean: 30.48 m) |
| **Road Network** | 598.34 km (993 segments) | Density: 2.69 km/km², Max road distance: 4.07 km |
| **Trafficability Class 1** | **30.96 km² (14.06%)** | High Trafficability (Slope $\le 10^\circ$, Low Ruggedness) |
| **Trafficability Class 2** | **85.77 km² (38.94%)** | Moderate Trafficability (Slope $10^\circ - 20^\circ$) |
| **Trafficability Class 3** | **64.44 km² (29.26%)** | Restricted Trafficability (Slope $20^\circ - 30^\circ$) |
| **Trafficability Class 4** | **39.06 km² (17.74%)** | Impassable Barrier (Slope $> 30^\circ$, Cliffs/Gorges) |
| **Visibility (5 km Zone)** | **8.81 km² (22.04%)** | Line-of-sight from 2,388m vantage ridge within 40.00 km² buffer |
| **Land Cover (Tree Cover)**| **149.72 km² (67.31%)** | ESA WorldCover 2021 (10m, reprojected to UTM 43N) |
| **Land Cover (Grassland)** | **58.87 km² (26.47%)** | High-altitude shola-grassland mosaic |
| **Land Cover (Settlements)**| **7.95 km² (3.57%)** | Built-up urban and rural settlement footprint |
| **Land Cover (Cropland/Tea)**| **5.77 km² (2.59%)** | Commercial tea and coffee plantation estates |
| **Spatial Database** | 7 tables, GiST indexed | PostgreSQL 18 / PostGIS 3.6.1 in schema `coonoor_geoai` |
| **ML Surrogate Accuracy** | **100.00%** | Random Forest Classifier trained on 244,705 cells |
| **Quality Audit Score** | **50 / 50 (100.0%)** | Fully validated in `07_Metadata/data_manifest.csv` |

---

## Interactive WebGIS Application

The project features a full-featured, dark-mode WebGIS interface accessible through any modern web browser or served via the included FastAPI backend.

### Features
- **Seamless Layer Toggling**: Digital Elevation Model, Analytical Hillshade, Slope Steepness, 4-Class Trafficability, Viewshed Analysis (5km buffer), and ESA WorldCover Land Cover.
- **Dynamic Opacity Controls**: Adjust raster layer transparency in real-time over 4 base maps (CartoDB Dark, Esri Satellite, OpenTopoMap, OpenStreetMap).
- **Vector Overlays**: Toggleable WGS84 GeoJSON vector boundaries for Coonoor Taluk AOI, 993-segment OSM road network, and observer vantage points with 5 km radius circles.
- **Interactive Statistical Charts**: Responsive horizontal bar charts displaying land cover, trafficability distribution, and road classification.
- **Dynamic Legends**: Context-sensitive legends with smooth continuous color ramps (Elevation, Slope) and discrete categorical palettes.
- **RESTful API Backend**: FastAPI server with automated Swagger/OpenAPI documentation at `http://localhost:8000/docs`.

### Launching the WebGIS Application
Double-click `start_app.bat` or run:
```powershell
python D:\Defence\MyProject1\start_backend.py
```
Then navigate to:
- **WebGIS Interface**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

Alternatively, open `D:\Defence\MyProject1\06_Outputs\Web_App\index.html` directly in any web browser.

---

## Directory Architecture

```
D:\Defence\MyProject1\
├── 01_AOI/                     # Validated boundary shapefiles and extents
├── 02_Raw_Data/                # Immutable downloaded Copernicus DEM, WorldCover & OSM GeoJSON
│   ├── DEM/
│   ├── LandCover/
│   └── OSM/
├── 03_Processed_Data/          # Projected (EPSG:32643) 30m analysis rasters & vectors
│   ├── DEM/                    # Elevation (elevation_32643.tif)
│   ├── Terrain/                # Slope (deg/pct), Aspect, Hillshade, Curvature, TRI, Trafficability
│   ├── LandCover/              # ESA WorldCover clipped (worldcover_coonoor_32643.tif)
│   ├── OSM/                    # Clipped road shapefiles
│   ├── Features/               # Road Euclidean distance proximity raster
│   └── Visibility/             # Observer vantage point, 5km buffer & Viewshed raster
├── 04_ArcGIS/                  # Packaged Coonoor_Analysis.aprx (non-destructive copy)
├── 05_Scripts/                 # Modular, numbered ArcPy/Python pipeline scripts
│   ├── 00_inspect_environment.py
│   ├── 01_validate_aoi.py
│   ├── 02_acquire_dem.py
│   ├── 03_process_terrain.py
│   ├── 03b_process_worldcover.py
│   ├── 04_acquire_osm.py
│   ├── 05_build_accessibility_index.py
│   ├── 06_visibility_analysis.py
│   ├── 07_validate_outputs.py
│   ├── 08_load_postgis.py
│   ├── 09_create_maps_and_report.py
│   ├── 10_generate_web_overlays.py
│   ├── 11_export_web_geojson.py
│   ├── backend_api.py
│   └── run_pipeline.py
├── 06_Outputs/                 # High-resolution publication deliverables & Web App
│   ├── Maps/                   # 300 DPI publication maps (PNG and vector PDF)
│   ├── Figures/                # Analytical statistical charts and histograms
│   ├── Tables/                 # Computed CSV summaries of areas, metrics, and road stats
│   ├── Web_Overlays/           # Georeferenced RGBA transparent PNG overlays & metadata
│   ├── Web_App/                # Standalone Leaflet WebGIS application (HTML/CSS/JS)
│   └── Reports/                # Technical reports and resume summaries
├── 07_Metadata/                # Complete data_manifest.csv of all 50 verified items
├── 08_Logs/                    # Detailed execution traces and quality audits
├── 09_Config/                  # config.json and local environment variables (.env)
├── 10_PostGIS/                 # Production DDL schema and GiST spatial indexes
├── 11_ML/                      # GeoAI Random Forest surrogate model, features, and evaluation
├── start_app.bat               # One-click Windows startup batch script
├── start_backend.py            # Cross-platform Python launcher for backend & WebGIS
├── methodology.md              # In-depth scientific and engineering methodology
├── limitations.md              # Explicit academic assumptions and safety disclosures
└── README.md                   # This project guide
```

---

## Quick Start & Pipeline Execution

### Prerequisites
- Windows 10/11 x64
- ArcGIS Pro 3.5 with Spatial Analyst extension (`D:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe`)
- Python 3.11 (with `fastapi`, `uvicorn`, `psycopg2`, `scikit-learn`, `matplotlib`, `pillow`)
- PostgreSQL 18 with PostGIS 3.6 (Running locally on port 5432)

### Single-Command Automated Run
Execute the entire pipeline end-to-end from scratch:
```powershell
& "D:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "D:\Defence\MyProject1\05_Scripts\run_pipeline.py"
```

---

## Cartographic Outputs Overview

1. **Map 01: Elevation & Analytical Hillshade** (`06_Outputs/Maps/Map_01_Elevation_Hillshade.png`)
   - Highlights the steep transition from the Mettupalayam foothills (413m) to the Doddabetta-Coonoor plateau (2,388m).
2. **Map 02: Topographic Slope Steepness** (`06_Outputs/Maps/Map_02_Slope_Steepness.png`)
   - Pinpoints escarpments, vertical cliff walls, and deep river gorges across 5 gradient classes.
3. **Map 03: Multi-Criteria Trafficability Classification** (`06_Outputs/Maps/Map_03_Terrain_Trafficability_Index.png`)
   - Categorizes landscape into 4 movement zones based on slope (60%), ruggedness (40%), and road proximity.
4. **Map 04: Topographic Viewshed & Line-of-Sight** (`06_Outputs/Maps/Map_04_Visibility_Viewshed_Demonstration.png`)
   - Analyzes line-of-sight intervisibility and topographic shadow zones across a 5.0 km radius from a dominant 2,388m vantage ridge.

---

## Data Quality & Audit Verification

The project underwent a rigorous 50-point automated quality assurance audit executed by `05_Scripts/07_validate_outputs.py`:
- **50 of 50 deliverables present, non-empty, and verified (100.0% compliance score)**.
- Full manifest logged in `07_Metadata/data_manifest.csv`.
- Full audit report logged in `08_Logs/data_quality_report.txt`.
- Database schema verified in `08_Logs/postgis_load_report.txt`.
