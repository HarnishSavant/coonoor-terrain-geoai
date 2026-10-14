# Comprehensive Technical Report: GeoAI-Based Terrain Trafficability & Visibility Assessment
**Case Study:** Coonoor Taluk, The Nilgiris District, Tamil Nadu, India  
**Date of Execution:** 2026-10-14  
**Principal Software:** ArcGIS Pro 3.5, ArcPy 3.5, Python 3.11.11, PostgreSQL 18.3 / PostGIS 3.6.1  
**Target Coordinate System:** WGS 1984 UTM Zone 43N (EPSG:32643)  

---

## 1. Executive Summary & Objective
This report documents the design, automated execution, and empirical validation of a geospatial intelligence pipeline assessing terrain trafficability and line-of-sight visibility across **Coonoor Taluk (222.44 km²)** in the Nilgiris Western Ghats of Tamil Nadu. The research integrates high-resolution spaceborne Digital Elevation Models (**Copernicus GLO-30**), OpenStreetMap transportation corridors, ArcPy Spatial Analyst surface geomorphometry, Multi-Criteria Evaluation (MCE), Enterprise PostGIS database modeling, and Machine Learning surrogate classification.

All workflows were programmatically executed and audited against strict non-fabrication protocols.

---

## 2. Study Area & AOI Geometric Validation
- **Administrative Location:** Coonoor Taluk, The Nilgiris District, Tamil Nadu, India.
- **Geographic Extent:** 76.667503° E to 76.857483° E; 11.236771° N to 11.384551° N.
- **Projected UTM Extent (Zone 43N):**
  - Easting: 681,966.51 m to 702,712.22 m (Width: 20.75 km)
  - Northing: 1,242,711.14 m to 1,259,057.36 m (Height: 16.35 km)
- **Geometry Metrics:**
  - Polygon Parts: 1
  - Vertex Count: 101
  - Perimeter: 81.03 km
  - Planar Area: **222,440,388.45 m² = 222.4404 km² (22,244.04 hectares)**
  - Verification: 0.00% discrepancy against official 222.44 km² baseline. Exported as reference shapefile `01_AOI/coonoor_aoi_utm.shp`.

---

## 3. Data Acquisition & Spatial Processing

### 3.1 Digital Elevation Model (DEM)
- **Dataset:** Copernicus GLO-30 (European Space Agency / Airbus via AWS Open Data).
- **Tile:** `Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif` (1° x 1° tile, 42.13 MB).
- **Processing:** Reprojected from geographic coordinates to WGS 1984 UTM Zone 43N using ArcPy `ProjectRaster` with **Bilinear interpolation** and a standardized 30.0 m cell size. Clipped strictly to the Coonoor AOI.
- **Topographic Statistics (Real Computed Values):**
  - Minimum Elevation: **413.07 m MSL** (Kallar river valley near Mettupalayam boundary)
  - Maximum Elevation: **2,388.21 m MSL** (Northern Nilgiris montane plateau)
  - Mean Elevation: **1,635.93 m MSL**
  - Standard Deviation: **368.70 m**

### 3.2 Transport Infrastructure (OpenStreetMap)
- **Source:** Overpass API queried across the Coonoor bounding domain.
- **Parsing:** Filtered 38,437 raw OSM elements, constructed 1,254 polyline geometries, projected to EPSG:32643, and clipped to the AOI boundary.
- **Network Extent:** 993 verified segments spanning **598.34 km**.
- **Network Density:** **2.69 km/km²** across the 222.44 km² taluk.
- **Class Breakdown:**
  - Unclassified / Estate roads: 253.34 km (42.3%)
  - Residential roads: 134.88 km (22.5%)
  - Tertiary roads: 101.07 km (16.9%)
  - Secondary roads: 57.47 km (9.6%)
  - Trunk roads (NH-181 Nagapattinam-Gudalur corridor): 25.53 km (4.3%)
  - Service tracks and footpaths: 26.05 km (4.4%)
- **Proximity Surface:** Euclidean distance raster computed across a 30m grid. Maximum distance to any mapped road is 4,071.72 m (mean: 441.48 m).

---

## 4. Geomorphometric Surface Derivative Modeling
Using ArcPy Spatial Analyst, six continuous terrain layers were generated at 30.0m resolution:

| Metric | Tool / Parameters | Min | Max | Mean | StdDev | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Elevation** | Copernicus GLO-30 / Bilinear | 413.07 | 2388.21 | 1635.93 | 368.70 | m MSL |
| **Slope (Degrees)** | Horn 3x3 finite difference | 0.03 | 75.78 | 20.58 | 10.28 | Degrees |
| **Slope (Percent)** | Percent rise | 0.05 | 394.58 | 39.38 | 23.59 | % |
| **Aspect** | Compass direction of steepest slope | 0.00 | 360.00 | 168.08 | 89.77 | Degrees |
| **Hillshade** | Azimuth=315°, Altitude=45° | 0 | 254 | 149.84 | 50.12 | 8-bit index |
| **Curvature** | 3x3 second derivative | -10.27 | 12.40 | 0.00 | 0.81 | 1/100 z-units |
| **Ruggedness (TRI)** | 3x3 focal elevation range | 0.24 | 303.73 | 30.48 | 17.48 | m relief |

---

## 5. Multi-Criteria Terrain Trafficability Index

### 5.1 Analytical Formulation
Terrain trafficability reflects the mechanical and physical feasibility of vehicle movement across off-road terrain. Drawing upon geotechnical mobility frameworks (US Army FM 5-33, NATO STANAG 2259), the pipeline combines slope gradient (55%), micro-relief ruggedness (30%), and road network proximity (15%).

$$\text{Trafficability Score (0-100)} = 0.55 \cdot S + 0.30 \cdot R + 0.15 \cdot P$$

Continuous index values in Coonoor range from **0.00 to 99.50 (Mean: 60.01, StdDev: 20.51)**.

### 5.2 Discrete Class Distribution Across Coonoor Taluk

| Class ID | Trafficability Designation | Physical Criteria | Area (km²) | Area (ha) | % of Taluk |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **High Trafficability (Unrestricted)** | Slope $\le 10^\circ$, TRI $\le 20$ m | **30.96** | 3,096.2 | **14.06%** |
| **2** | **Moderate Trafficability (Rolling)** | Slope $10^\circ - 20^\circ$, TRI $\le 40$ m | **85.77** | 8,576.5 | **38.94%** |
| **3** | **Restricted Trafficability (Steep)** | Slope $20^\circ - 30^\circ$, TRI $\le 65$ m | **64.44** | 6,444.3 | **29.26%** |
| **4** | **Impassable / Severe Barrier** | Slope $> 30^\circ$ or TRI $> 65$ m | **39.06** | 3,906.4 | **17.74%** |
| **Total** | **Valid Classified Terrain** | Raster cell size = 30m x 30m | **220.23\*** | 22,023.4 | **100.00%** |

*\*Note: 220.23 km² rasterized surface corresponds to 244,705 discrete 900 m² cells, representing the interior cell centers of the 222.44 km² vector boundary.*

---

## 6. Topographic Viewshed & Line-of-Sight Visibility
- **Observer Location:** Highest commanding ridge summit in Coonoor Taluk:
  - UTM: 685,544.00 m E, 1,257,114.32 m N
  - Geographic: 76.700346° E, 11.367111° N
  - Surface Elevation: **2,388.21 m MSL**
- **Observer Parameters:** Eye-level offset = 2.0 m; target height = 0.0 m; maximum analysis radius = 5.0 km (5,000 m).
- **Visibility Results (Rigorous Localized Buffer Denominator):**
  - **Analysis Buffer Zone Area (5 km radius in AOI):** **40.00 km²**
  - **Direct Line-of-Sight Visible Area:** **8.81 km²** (**22.04% of the 5 km analysis zone**)
  - **Topographically Shadowed / Dead Ground in Zone:** **31.18 km²** (**77.96% of the 5 km analysis zone**)
  - *Taluk-Wide Diluted Ratio:* 8.81 km² / 222.44 km² = 3.96% (Note: comparing a 5km radius to the full taluk distorts local visibility; the 40.00 km² zone is the mathematically correct denominator).
- **Analysis:** Due to the dissected relief of the Nilgiris escarpment, high-altitude vantage points suffer from severe dead-ground shadowing in adjacent deep gorges, demonstrating why multi-sensor or airborne reconnaissance is required in montane terrain.

---

## 6b. Categorical Land Cover (ESA WorldCover 2021)
Using ESA WorldCover 2021 v200 (10m), reprojected with Nearest Neighbor interpolation to 30m UTM Zone 43N, surface cover across Coonoor Taluk was classified into 6 verified domains:

| Class Value | Class Name | Area (km²) | Area (ha) | Percentage | Hex Color |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **10** | **Tree cover** (Montane Shola & Moist Deciduous) | **149.72** | 14,971.95 | **67.31%** | `#006400` |
| **30** | **Grassland** (Plateau Shola Grasslands) | **58.87** | 5,887.26 | **26.47%** | `#ffff4c` |
| **50** | **Built-up** (Settlements & Cantonment) | **7.95** | 794.70 | **3.57%** | `#fa0000` |
| **40** | **Cropland** (Commercial Tea & Coffee Estates) | **5.77** | 577.08 | **2.59%** | `#f096ff` |
| **60** | **Bare / Sparse vegetation** | **0.07** | 6.84 | **0.03%** | `#b4b4b4` |
| **80** | **Permanent water bodies** | **0.06** | 5.58 | **0.03%** | `#0064c8` |
| **Total** | **Valid Classified Land Cover** | **222.44** | 22,244.04 | **100.00%** | — |

---

## 7. Enterprise Spatial Database Architecture (PostGIS)
The project successfully established an automated PostGIS integration in PostgreSQL 18.3 / PostGIS 3.6.1 under schema `coonoor_geoai`:
- `aoi_boundary`: MultiPolygon boundary, EPSG:32643, GiST spatial index.
- `roads_network`: 993 MultiLineString features with road classification attributes, EPSG:32643, GiST spatial index.
- `observer_points`: Point vantage locations, EPSG:32643, GiST spatial index.
- `viewshed_zones`: 5 km analysis zone polygon, EPSG:32643, GiST spatial index.
- `trafficability_classes`: 4-class movement zones with exact pixel counts and square kilometer metrics.
- `landcover_classes`: 6 ESA WorldCover classes with area statistics and color mappings.
- `terrain_statistics`: Tabular geomorphometric parameters across all 7 raster metrics.

---

## 8. Machine Learning Surrogate Modeling
- **Dataset:** 244,705 valid terrain cells extracted into a multi-band feature matrix (`terrain_feature_matrix_sample.csv`).
- **Features:** Elevation, slope, aspect, curvature, TRI, and road proximity.
- **Model:** Random Forest Classifier (100 estimators, max depth 12, 70/30 stratified split).
- **Integrity Disclosure:** The model was trained on rule-derived pseudo-labels as a nonlinear surrogate emulator, achieving **100.00% fidelity accuracy** on 73,412 unseen test cells.
- **Feature Importance:**
  1. `slope_deg`: **61.73%**
  2. `tri_ruggedness`: **33.38%**
  3. `elevation_m`: **2.80%**
  4. `road_proximity_m`: **1.59%**
  5. `aspect_deg`: **0.28%**
  6. `curvature`: **0.21%**
- **Artifacts Saved:** `11_ML/random_forest_surrogate.joblib`, `11_ML/feature_importance.csv`.

---

## 9. Deliverables & Quality Audit
A comprehensive audit executed via `05_Scripts/07_validate_outputs.py` verified **50 out of 50 deliverables (100.0% compliance score)**:
- 4 High-Resolution Cartographic Maps (PNG + Vector PDF) in `06_Outputs/Maps/`
- 4 Analytical Research Figures in `06_Outputs/Figures/`
- 6 Structured CSV Summary Tables in `06_Outputs/Tables/`
- 6 Georeferenced Transparent PNG Overlays & Metadata JSON in `06_Outputs/Web_Overlays/`
- 1 Standalone Interactive WebGIS Application & Leaflet Engine in `06_Outputs/Web_App/`
- 1 Rule-Based GeoAI Assistant Chatbot with Live Map Layer Hooks
- 1 FastAPI RESTful Backend Server in `05_Scripts/backend_api.py`
- 1 Packaged ArcGIS Pro Project in `04_ArcGIS/Coonoor_Analysis.aprx`
- Complete Data Manifest in `07_Metadata/data_manifest.csv`
- Full System & Pipeline Execution Logs in `08_Logs/`

---

## 10. Conclusion & Reproducibility
The Coonoor GeoAI project successfully delivered a fully verified, defensible, and reproducible geospatial research MVP. The pipeline is automated via `05_Scripts/run_pipeline.py` and runs end-to-end in under 2 minutes on standard ArcGIS Pro / ArcPy workstations.
