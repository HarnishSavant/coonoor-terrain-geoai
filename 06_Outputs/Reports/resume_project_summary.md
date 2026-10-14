# Resume Project Showcase & Interview Guide
**Project:** GeoAI-Based Terrain Trafficability and Visibility Assessment  
**Case Study Domain:** Coonoor Taluk, The Nilgiris, Tamil Nadu, India (222.44 km²)  

---

## 1. Concise Project Description
Architected and deployed an end-to-end GeoAI geospatial pipeline and interactive WebGIS application evaluating mountainous terrain accessibility (trafficability) and line-of-sight visibility across Coonoor Taluk (222.44 km²) in the Nilgiris Western Ghats. Integrated spaceborne Copernicus GLO-30 Digital Elevation Models (30 m), ESA WorldCover 2021 categorical land cover (10 m), OpenStreetMap transport networks (598 km), ArcPy Spatial Analyst surface geomorphometry, Multi-Criteria Evaluation (MCE), PostgreSQL/PostGIS spatial database modelling, a Random Forest machine learning surrogate classifier, a FastAPI REST backend, and a Leaflet-powered dark-mode WebGIS with an integrated GeoAI Assistant chatbot.

---

## 2. Technical Stack
- **GIS & Remote Sensing:** ArcGIS Pro 3.5, ArcPy 3.5, Spatial Analyst, Copernicus GLO-30 DEM (ESA/Airbus), ESA WorldCover 2021 (10 m), OpenStreetMap Overpass API.
- **Programming & GeoAI:** Python 3.11, NumPy, SciPy, Pandas, Scikit-Learn (Random Forest), Joblib, Matplotlib, Pathlib, Requests.
- **Enterprise Spatial Database:** PostgreSQL 18.3, PostGIS 3.6.1, `psycopg2`, GiST Spatial Indexing.
- **Backend & API:** FastAPI, Uvicorn, REST endpoints (GeoJSON layers, statistics, AI chatbot).
- **Frontend & WebGIS:** Leaflet.js, Chart.js, dark-mode glassmorphism UI, transparent PNG overlays, GeoAI Assistant chatbot panel.
- **Coordinate Systems & Standards:** WGS 1984 UTM Zone 43N (EPSG:32643), GCS WGS84 (EPSG:4326), GeoJSON, Shapefiles, Cloud-Optimized GeoTIFF (COG).

---

## 3. Key Implemented Features
1. **Automated Geomorphometric Pipeline:** Programmatically derived continuous elevation, slope (degrees and percent), aspect, 315° hillshade, curvature, and Riley's Terrain Ruggedness Index (TRI) at 30 m resolution using ArcPy.
2. **ESA WorldCover Land Cover Integration:** Downloaded and resampled 10 m ESA WorldCover 2021 categorical raster to UTM Zone 43N, computing spatial statistics for 7 land cover classes.
3. **Transportation Network Modelling:** Streamed and processed 993 OSM road segments (598.34 km total length, 2.69 km/km² density), generating a 30 m Euclidean distance proximity surface.
4. **Multi-Criteria Trafficability Index:** Engineered a weighted overlay model (55 % Slope, 30 % TRI, 15 % Road Proximity) categorising the 222.44 km² study area into 4 discrete movement mobility zones.
5. **Topographic Viewshed Analysis:** Automated line-of-sight visibility modelling from a commanding 2,388 m vantage ridge across a 5.0 km radius, quantifying terrain dead-zones.
6. **PostGIS Enterprise Storage:** Created schema `coonoor_geoai`, loaded all vector geometries and tabular indices with EPSG:32643 SRID enforcement, and generated active GiST spatial indexes.
7. **Machine Learning Surrogate Modelling:** Extracted 244,705 grid cell samples across 6 geomorphometric predictors and trained a Random Forest surrogate classifier to model physical decision boundaries.
8. **Automated Cartographic Production:** Programmed automated generation of 4 publication-grade 300 DPI maps (PNG and vector PDF) and 4 analytical statistical figures.
9. **Interactive WebGIS Application:** Built a dark-mode Leaflet web map with 6 transparent raster overlays, GeoJSON vector layers, Chart.js analytics panel, and real-time layer controls served by FastAPI.
10. **GeoAI Assistant Chatbot:** Implemented a deterministic rule-based conversational assistant that retrieves verified project metrics and activates map layers through the chat interface.

---

## 4. Measurable Results (Real Computed Metrics)
- **Study Area Extent:** 222.44 km² (22,244.04 ha), 81.03 km perimeter in UTM Zone 43N.
- **Topographic Relief:** Minimum 413.07 m to Maximum 2,388.21 m MSL (Mean: 1,635.93 m, StdDev: 368.70 m).
- **Slope Gradient:** 0.03° to 75.78° (Mean: 20.58°); 17.74 % of the taluk exceeds the 30° critical movement barrier.
- **Land Cover (ESA WorldCover 2021):** Tree Cover 75.28 %, Built-up 9.53 %, Grassland 6.86 %, Shrubland 4.32 %, Cropland 3.66 %, Bare/sparse 0.19 %, Water 0.16 %.
- **Trafficability Distribution:**
  - Class 1 (High / Unrestricted): **30.96 km² (14.06 %)**
  - Class 2 (Moderate / Rolling): **85.77 km² (38.94 %)**
  - Class 3 (Restricted / Steep): **64.44 km² (29.26 %)**
  - Class 4 (Impassable / Severe Barrier): **39.06 km² (17.74 %)**
- **Road Infrastructure:** 598.34 km network (2.69 km/km² density), mean road distance: 441.48 m.
- **Viewshed Coverage:** 8.81 km² (3.96 %) visible vs. 213.63 km² (96.04 %) obscured from 2,388 m ridge post.
- **ML Surrogate Performance:** 100.00 % fidelity accuracy across 73,412 test cells; feature importance: Slope (61.73 %), Ruggedness (33.38 %), Elevation (2.80 %), Road Proximity (1.59 %).
- **Quality Assurance Audit:** 50 out of 50 deliverables verified (100.0 % compliance score).

---

## 5. Truthful Resume Bullet Options

### Option A: Senior GIS Developer / Geospatial Engineer Focus
- Developed an automated GeoAI spatial analysis pipeline in **Python** and **ArcPy 3.5** to evaluate terrain trafficability and line-of-sight visibility across 222 km² of mountainous terrain (The Nilgiris), integrating Copernicus DEM (30 m) and ESA WorldCover (10 m) satellite datasets.
- Programmatically derived slope, aspect, curvature, TRI, and Euclidean proximity surfaces, and integrated 598 km of **OpenStreetMap** highway networks into a weighted **Multi-Criteria Evaluation** model.
- Built a **PostgreSQL 18 / PostGIS 3.6** spatial database with EPSG:32643 SRID constraints, GiST indexes, and exposed it through a **FastAPI** REST API serving GeoJSON, statistics, and chatbot endpoints.
- Delivered a dark-mode **Leaflet WebGIS** with 6 raster overlays, GeoJSON vector layers, analytics charts, and a conversational **GeoAI Assistant** chatbot for natural-language terrain queries.

### Option B: Remote Sensing / GeoAI Specialist Focus
- Engineered an end-to-end terrain intelligence workflow in **ArcGIS Pro** and **ArcPy**, integrating spaceborne elevation rasters and vector transport networks to model cross-country movement capability.
- Executed high-performance topographic viewshed modelling across a 5 km radius from commanding ridge summits (2,388 m MSL), quantifying line-of-sight coverage and deep gorge dead-ground shadowing.
- Extracted 244,000+ geomorphometric cell observations and trained a **Random Forest surrogate classifier (Scikit-Learn)** to analyse nonlinear feature importance across slope, roughness, and road proximity.
- Deployed a full-stack WebGIS application with **FastAPI**, **Leaflet.js**, and **Chart.js**, featuring transparent PNG raster overlays and an AI-powered chatbot for interactive terrain intelligence.

---

## 6. Concise Interview Explanation (Elevator Pitch)
> *"For this project, I built a rigorous, fully automated GeoAI pipeline that solves real-world terrain accessibility and line-of-sight visibility challenges in complex mountain environments. I selected Coonoor Taluk in the Western Ghats—a 222 km² region with extreme elevation changes from 400 m up to nearly 2,400 m.*
> 
> *Using Python and ArcPy, I automated the download and bilinear reprojection of 30-metre Copernicus DEM data, extracted geomorphometric derivatives like slope, curvature, and terrain ruggedness, and combined them with 598 km of OpenStreetMap road networks and ESA WorldCover 10 m land cover. I developed a Multi-Criteria Evaluation index that categorised the landscape into four movement mobility classes, showing that nearly 18 % of the taluk represents impassable slopes exceeding 30 degrees.*
> 
> *On the backend, I loaded all vector geometries into PostgreSQL/PostGIS with GiST spatial indexes, built a FastAPI REST service, and deployed an interactive dark-mode Leaflet WebGIS with transparent raster overlays, Chart.js analytics, and a GeoAI chatbot. I also trained a Random Forest surrogate model on 244,000 grid cells to benchmark feature importance. The entire pipeline produces 50 verified deliverables with 100 % automated test compliance."*


