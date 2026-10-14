-- ====================================================================
-- Coonoor GeoAI Database Schema (PostgreSQL 18 / PostGIS 3.6)
-- Spatial Reference System: EPSG:32643 (WGS 1984 / UTM Zone 43N)
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS coonoor_geoai;

-- 1. Study Area (AOI) Boundary
CREATE TABLE IF NOT EXISTS coonoor_geoai.aoi_boundary (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    taluk VARCHAR(50) DEFAULT 'Coonoor',
    district VARCHAR(50) DEFAULT 'The Nilgiris',
    state VARCHAR(50) DEFAULT 'Tamil Nadu',
    area_sqkm DOUBLE PRECISION,
    perimeter_km DOUBLE PRECISION,
    geom GEOMETRY(MultiPolygon, 32643)
);

CREATE INDEX IF NOT EXISTS idx_aoi_geom 
ON coonoor_geoai.aoi_boundary USING GIST (geom);

-- 2. Road and Path Network
CREATE TABLE IF NOT EXISTS coonoor_geoai.roads_network (
    id SERIAL PRIMARY KEY,
    osm_id VARCHAR(50),
    highway_class VARCHAR(50),
    name VARCHAR(100),
    surface VARCHAR(50),
    length_m DOUBLE PRECISION,
    geom GEOMETRY(MultiLineString, 32643)
);

CREATE INDEX IF NOT EXISTS idx_roads_geom 
ON coonoor_geoai.roads_network USING GIST (geom);

-- 3. Viewshed Observer Locations
CREATE TABLE IF NOT EXISTS coonoor_geoai.observer_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    elevation_m DOUBLE PRECISION,
    observer_height_m DOUBLE PRECISION,
    target_height_m DOUBLE PRECISION,
    max_radius_m DOUBLE PRECISION,
    geom GEOMETRY(Point, 32643)
);

CREATE INDEX IF NOT EXISTS idx_observer_geom 
ON coonoor_geoai.observer_points USING GIST (geom);

-- 4. Trafficability Classes Summary Table
CREATE TABLE IF NOT EXISTS coonoor_geoai.trafficability_classes (
    class_id INT PRIMARY KEY,
    class_name VARCHAR(150) NOT NULL,
    pixel_count BIGINT,
    area_sqm DOUBLE PRECISION,
    area_ha DOUBLE PRECISION,
    area_sqkm DOUBLE PRECISION,
    percentage DOUBLE PRECISION,
    description TEXT
);

-- 5. Land Cover (ESA WorldCover 2021) Classes Table
CREATE TABLE IF NOT EXISTS coonoor_geoai.landcover_classes (
    class_value INT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    hex_color VARCHAR(10),
    pixel_count BIGINT,
    area_sqkm DOUBLE PRECISION,
    area_ha DOUBLE PRECISION,
    percentage DOUBLE PRECISION
);

-- 6. Viewshed 5km Analysis Zone
CREATE TABLE IF NOT EXISTS coonoor_geoai.viewshed_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    radius_m DOUBLE PRECISION,
    area_sqkm DOUBLE PRECISION,
    visible_sqkm DOUBLE PRECISION,
    obscured_sqkm DOUBLE PRECISION,
    visibility_percentage DOUBLE PRECISION,
    geom GEOMETRY(MultiPolygon, 32643)
);

CREATE INDEX IF NOT EXISTS idx_viewshed_zone_geom 
ON coonoor_geoai.viewshed_zones USING GIST (geom);

-- 7. Geomorphometric Surface Metrics Table
CREATE TABLE IF NOT EXISTS coonoor_geoai.terrain_statistics (
    metric_name VARCHAR(50) PRIMARY KEY,
    raster_file VARCHAR(100),
    units VARCHAR(50),
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    mean_value DOUBLE PRECISION,
    std_dev DOUBLE PRECISION,
    resolution_m DOUBLE PRECISION,
    srid INT DEFAULT 32643
);
