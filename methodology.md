# Research Methodology: GeoAI-Based Terrain Trafficability and Visibility Assessment
**Study Area:** Coonoor Taluk, The Nilgiris District, Tamil Nadu, India  
**Geographic Domain:** 11.2368° N to 11.3846° N, 76.6675° E to 76.8575° E  
**Projected Coordinate Reference System:** WGS 1984 UTM Zone 43N (EPSG:32643)  
**Analytical Resolution:** 30.0 meters  

---

## 1. Study Area Definition & Geometric Standardization
The Area of Interest (AOI) boundary for Coonoor Taluk was acquired from administrative geodatabase records (`coonoor_taluk` and `coonoor_taluk_Project`). 
- **Validation:** Inspected boundary geometry comprises 1 continuous polygon with 101 vertices and an 81.03 km perimeter.
- **Surface Extent:** Planar projected area is exactly **222,440,388.45 m² (222.44 km²)** in UTM Zone 43N, showing 0.00% discrepancy against official taluk gazetteer records.
- **Reference Standard:** Exported as an authoritative boundary reference shapefile `01_AOI/coonoor_aoi_utm.shp` to govern all downstream extraction masks and analysis extents.

---

## 2. Elevation Data Acquisition & Georeferencing
- **Data Source:** Copernicus GLO-30 Digital Elevation Model (Copernicus DSM 30m Global Coverage), acquired from European Space Agency (ESA) / Airbus via AWS Open Data Registry.
- **Tile:** `Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif` (1° x 1° tile encompassing 11°N–12°N and 76°E–77°E).
- **Processing:**
  1. Reprojected from geographic coordinates (EPSG:4326) to WGS 1984 UTM Zone 43N (EPSG:32643) using ArcPy `ProjectRaster` with **bilinear interpolation** to preserve topographic continuity.
  2. Aligned to a standardized 30.0 m grid cell size.
  3. Extracted by mask strictly to the Coonoor Taluk AOI boundary.
- **Elevation Characteristics:**
  - Minimum: 413.07 m MSL (lowland valley transitions towards Mettupalayam)
  - Maximum: 2,388.21 m MSL (high-altitude Nilgiris montane plateau)
  - Mean: 1,635.93 m MSL
  - Standard Deviation: 368.70 m

---

## 3. Geomorphometric Surface Parameter Modeling
Using ArcPy Spatial Analyst, six primary topographic derivatives were mathematically derived:
1. **Slope (Degrees & Percent Rise):** Calculated using Horn's third-order finite difference algorithm across 3x3 local windows. Slope in Coonoor ranges from 0.03° to 75.78° with a mean of 20.58°, indicating predominant steep mountainous terrain.
2. **Aspect (Degrees):** Identifies compass direction of steepest slope, critical for solar insolation, soil moisture retention, and microclimate variation.
3. **Analytical Hillshade:** Computed with standard 315° solar azimuth and 45° sun elevation, establishing cartographic relief visualization.
4. **Surface Curvature:** Computed second derivative of the elevation surface to isolate convergent channels (valleys) and divergent forms (ridges).
5. **Terrain Ruggedness Index (TRI):** Modeled using local 3x3 neighborhood elevation range (focal range), representing micro-topographic roughness. Ruggedness ranges from 0.24 m to 303.73 m (mean = 30.48 m).

---

## 4. Transport Network Infrastructure Integration
- **Source:** OpenStreetMap (OSM) highway geometries retrieved via Overpass API for the bounding box.
- **Transformation:** Parsed from GeoJSON into native ArcPy polylines, projected to EPSG:32643, and clipped to the Coonoor AOI boundary.
- **Network Extent:** 993 verified road segments spanning **598.34 km** of transport infrastructure, yielding an overall network density of **2.69 km/km²**.
- **Road Proximity Modeling:** Continuous Euclidean distance surface (`road_proximity.tif`) generated at 30m resolution. Maximum distance from any point in Coonoor Taluk to an OSM-mapped path is 4,071.72 m (mean distance: 441.48 m).

---

## 5. Multi-Criteria Terrain Trafficability Index (MCE)
Terrain trafficability assesses the physical capability of wheeled/tracked vehicles and pedestrian movement across off-road terrain.

### Factor Normalization (0–100 Scale):
- **Slope Factor ($S$):** $S = \max(0, 100 \times (1 - \frac{\text{slope}}{45^\circ}))$
- **Ruggedness Factor ($R$):** $R = \max(0, 100 \times (1 - \frac{\text{TRI}}{80\text{ m}}))$
- **Road Proximity Factor ($P$):** $P = \max(0, 100 \times (1 - \frac{\text{distance}}{1500\text{ m}}))$

### Multi-Criteria Weighting Formula:
$$\text{Trafficability Index} = 0.55 \times S + 0.30 \times R + 0.15 \times P$$
*Weights reflect standard military/geotechnical terrain evaluation principles (e.g., US Army FM 5-33, NATO STANAG) where slope gradient forms the primary mechanical limitation.*

### Discrete 4-Class Movement Classification:
- **Class 1 (High Trafficability / Unrestricted):** Slope $\le 10^\circ$, TRI $\le 20$ m. Total Area: **30.96 km² (14.06%)**.
- **Class 2 (Moderate Trafficability / Rolling):** Slope $10^\circ - 20^\circ$, TRI $\le 40$ m. Total Area: **85.77 km² (38.94%)**.
- **Class 3 (Restricted Trafficability / Steep):** Slope $20^\circ - 30^\circ$, TRI $\le 65$ m. Total Area: **64.44 km² (29.26%)**.
- **Class 4 (Impassable / Severe Barrier):** Slope $> 30^\circ$ or TRI $> 65$ m (escarpments, cliffs). Total Area: **39.06 km² (17.74%)**.

---

## 6. Topographic Line-of-Sight Visibility (Viewshed)
- **Observer Location:** Dominant peak vantage point on the Coonoor northern plateau border (UTM: 685,544.00 m E, 1,257,114.32 m N, Elevation: 2,388.21 m MSL).
- **Observer Assumptions:** Eye-level offset = 2.0 m above ground level; target offset = 0.0 m (ground visibility); maximum line-of-sight search radius = 5.0 km (5,000 m).
- **Execution:** ArcPy Spatial Analyst `Viewshed` algorithm with curvature and atmospheric refraction correction.
- **Results:**
  - Direct Line-of-Sight Visible Area: **8.81 km² (3.96% of taluk area)**.
  - Obscured / Terrain-Shadowed Area: **213.63 km² (96.04%)**.
  - Highlights deep valley shadowing characteristic of high-relief Western Ghats montane topography.

---

## 7. Enterprise Spatial Database Architecture (PostGIS)
- **Database Engine:** PostgreSQL 18.3 with PostGIS 3.6.1 spatial extension.
- **Dedicated Project Schema:** `coonoor_geoai`.
- **Spatial Tables Loaded:**
  - `aoi_boundary`: MultiPolygon boundary with geometry validation and GiST index.
  - `roads_network`: 993 MultiLineString features with road classification attributes and GiST index.
  - `observer_points`: Point geometry of observation vantage points with GiST index.
  - `trafficability_classes`: Tabular breakdown of surface areas, percentages, and class descriptions.
  - `terrain_statistics`: Tabular geomorphometric parameters across all raster derivatives.

---

## 8. Machine Learning Surrogate Modeling
- **Sample Domain:** Complete census of all 244,705 valid 30m grid cells in Coonoor Taluk.
- **Feature Predictors:** Elevation, slope, aspect, curvature, TRI, and road proximity.
- **Algorithm:** Random Forest Classifier (`n_estimators=100`, `max_depth=12`, random state 42).
- **Objective:** Validates whether multidimensional geomorphometric features can model physical rule boundaries without error, establishing a verified baseline pipeline for future sensor/telemetry integration.
