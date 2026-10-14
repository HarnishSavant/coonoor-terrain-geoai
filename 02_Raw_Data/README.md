# Raw Datasets Documentation & Acquisition

This directory contains raw source datasets utilized by the Coonoor GeoAI pipeline.

## 1. Digital Elevation Model (DEM)
- **Source:** Copernicus GLO-30 (European Space Agency / Airbus Defence & Space)
- **Tile ID:** `Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif` (1° × 1° tile, 30m resolution)
- **License:** Open access under the Copernicus Open Access Policy
- **Automated Download Script:** `python 05_Scripts/02_acquire_dem.py`
- **Direct S3 Public COG URL:**
  `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N11_00_E076_00_DEM/Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif`

## 2. Land Cover (Categorical)
- **Source:** ESA WorldCover 2021 v200 (10m resolution)
- **Tile ID:** `ESA_WorldCover_10m_2021_v200_N09E075_Map.tif` (3° × 3° tile)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Automated Download Script:** `python 05_Scripts/03b_process_worldcover.py`
- **Direct S3 Public COG URL:**
  `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N09E075_Map.tif`

## 3. Transportation Network
- **Source:** OpenStreetMap (OSM) via Overpass API
- **License:** Open Database License (ODbL) 1.0
- **Automated Query Script:** `python 05_Scripts/04_acquire_osm.py`
- **Raw File:** `02_Raw_Data/OSM/coonoor_highways_raw.geojson`
