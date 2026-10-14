"""
Script 04: Acquire and Process OpenStreetMap Road/Trail Network
Acquires OSM highway ways in Coonoor Taluk bounds, converts to native ArcPy Polyline features,
projects to EPSG:32643 (UTM Zone 43N), clips to AOI,
calculates road network length/density, and computes Euclidean distance raster.
"""
import sys
import os
import json
import time
from pathlib import Path
import requests
import arcpy

arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

aoi_shp = config["aoi"]["output_shp"]
roads_raw_geojson = Path(config["osm"]["roads_raw_geojson"])
roads_utm_shp = Path(config["osm"]["roads_shp"])
road_proximity_raster = Path(config["osm"]["road_proximity_raster"])

roads_raw_geojson.parent.mkdir(parents=True, exist_ok=True)
roads_utm_shp.parent.mkdir(parents=True, exist_ok=True)
road_proximity_raster.parent.mkdir(parents=True, exist_ok=True)

logs_dir = PROJECT_ROOT / "08_Logs"
tables_dir = PROJECT_ROOT / "06_Outputs" / "Tables"

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("OPENSTREETMAP ROAD/TRAIL NETWORK ACQUISITION & PROCESSING")
log("=" * 60)

# Check if GeoJSON already downloaded, otherwise fetch from Overpass
if roads_raw_geojson.exists() and roads_raw_geojson.stat().st_size > 10000:
    log(f"Loading existing raw OSM GeoJSON: {roads_raw_geojson}")
    with open(roads_raw_geojson, "r", encoding="utf-8") as f:
        geojson_doc = json.load(f)
else:
    south, west, north, east = 11.230, 76.660, 11.390, 76.865
    overpass_query = f"""
    [out:json][timeout:60];
    (
      way["highway"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """

    overpass_endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass.private.coffee/api/interpreter"
    ]

    headers = {
        "User-Agent": "CoonoorAcademicResearch/1.0 (academic; nilgiris-gis-research)",
        "Accept": "application/json"
    }

    osm_data = None
    for endpoint in overpass_endpoints:
        try:
            log(f"Attempting query to Overpass endpoint: {endpoint}")
            resp = requests.post(endpoint, data={"data": overpass_query}, headers=headers, timeout=35)
            if resp.status_code == 200:
                osm_data = resp.json()
                log(f"Successfully received OSM data: {len(osm_data.get('elements', []))} elements.")
                break
        except Exception as e:
            log(f"  Endpoint error: {e}, trying next...")
            time.sleep(1)

    if not osm_data or "elements" not in osm_data:
        log("ERROR: Could not retrieve OSM road network from any endpoint.")
        sys.exit(1)

    nodes = {}
    ways = []
    for el in osm_data["elements"]:
        if el["type"] == "node":
            nodes[el["id"]] = (el["lon"], el["lat"])
        elif el["type"] == "way":
            ways.append(el)

    features = []
    for way in ways:
        way_nodes = way.get("nodes", [])
        coords = [nodes[nid] for nid in way_nodes if nid in nodes]
        if len(coords) >= 2:
            tags = way.get("tags", {})
            props = {
                "osm_id": str(way["id"]),
                "highway": tags.get("highway", "unclassified"),
                "name": tags.get("name", ""),
                "surface": tags.get("surface", ""),
                "oneway": tags.get("oneway", ""),
                "maxspeed": tags.get("maxspeed", "")
            }
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": props
            }
            features.append(feature)

    geojson_doc = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(roads_raw_geojson, "w", encoding="utf-8") as f:
        json.dump(geojson_doc, f, indent=2)
    log(f"Saved {len(features)} road/track features to: {roads_raw_geojson}")

# Insert features into temporary feature class in GDB (EPSG:4326)
gdb = str(PROJECT_ROOT / "MyProject1.gdb")
fc_wgs = f"{gdb}\\coonoor_roads_wgs84"
fc_utm = f"{gdb}\\coonoor_roads_utm_all"

arcpy.env.overwriteOutput = True
if arcpy.Exists(fc_wgs):
    arcpy.management.Delete(fc_wgs)

sr4326 = arcpy.SpatialReference(4326)
arcpy.management.CreateFeatureclass(gdb, "coonoor_roads_wgs84", "POLYLINE", spatial_reference=sr4326)
arcpy.management.AddField(fc_wgs, "osm_id", "TEXT", field_length=50)
arcpy.management.AddField(fc_wgs, "highway", "TEXT", field_length=50)
arcpy.management.AddField(fc_wgs, "name", "TEXT", field_length=100)
arcpy.management.AddField(fc_wgs, "surface", "TEXT", field_length=50)

fields = ["SHAPE@", "osm_id", "highway", "name", "surface"]
with arcpy.da.InsertCursor(fc_wgs, fields) as cur:
    for feat in geojson_doc.get("features", []):
        coords = feat["geometry"]["coordinates"]
        props = feat.get("properties", {})
        pts = arcpy.Array([arcpy.Point(pt[0], pt[1]) for pt in coords])
        line = arcpy.Polyline(pts, sr4326)
        cur.insertRow([
            line,
            str(props.get("osm_id", ""))[:50],
            str(props.get("highway", "unclassified"))[:50],
            str(props.get("name", ""))[:100],
            str(props.get("surface", ""))[:50]
        ])

log(f"Imported {len(geojson_doc['features'])} line features into WGS84 feature class.")

# Project to UTM Zone 43N (EPSG:32643)
if arcpy.Exists(fc_utm):
    arcpy.management.Delete(fc_utm)

log("Projecting road features to WGS 1984 UTM Zone 43N (EPSG:32643)...")
arcpy.management.Project(fc_wgs, fc_utm, arcpy.SpatialReference(32643))

# Clip to AOI shapefile
if arcpy.Exists(str(roads_utm_shp)):
    arcpy.management.Delete(str(roads_utm_shp))

log(f"Clipping road network to Coonoor AOI: {aoi_shp}...")
arcpy.analysis.Clip(fc_utm, aoi_shp, str(roads_utm_shp))

count_clipped = int(arcpy.management.GetCount(str(roads_utm_shp))[0])
log(f"Total clipped road segments inside Coonoor AOI: {count_clipped}")

# Calculate road length and breakdown
class_lengths = {}
total_length_m = 0.0

with arcpy.da.SearchCursor(str(roads_utm_shp), ["highway", "SHAPE@LENGTH"]) as cursor:
    for row in cursor:
        hw_type = row[0] or "unclassified"
        l_m = row[1]
        total_length_m += l_m
        class_lengths[hw_type] = class_lengths.get(hw_type, 0.0) + l_m

total_length_km = total_length_m / 1000.0
aoi_area_sqkm = 222.44
road_density = total_length_km / aoi_area_sqkm

log("\n" + "=" * 60)
log("COONOOR ROAD NETWORK METRICS")
log("=" * 60)
log(f"Total Network Length: {total_length_km:.2f} km")
log(f"Study Area: {aoi_area_sqkm:.2f} km²")
log(f"Road Density: {road_density:.2f} km/km²")
log("\nLength by Classification:")

csv_lines = ["Highway_Class,Length_km,Percentage,Density_km_per_sqkm"]
for hw, length in sorted(class_lengths.items(), key=lambda x: x[1], reverse=True):
    l_km = length / 1000.0
    pct = (l_km / total_length_km) * 100 if total_length_km > 0 else 0
    d = l_km / aoi_area_sqkm
    log(f"  {hw:20}: {l_km:8.2f} km ({pct:5.1f}%)")
    csv_lines.append(f"{hw},{l_km:.2f},{pct:.2f},{d:.4f}")

# Compute Euclidean Distance to Roads (Cell Size = 30m)
log(f"\nComputing Euclidean Distance to Roads (Cell Size = 30m)...")
dem_path = config["dem"]["processed_dem_path"]
arcpy.env.extent = dem_path
arcpy.env.snapRaster = dem_path
arcpy.env.cellSize = 30.0
arcpy.env.mask = aoi_shp

euc_dist = EucDistance(str(roads_utm_shp), cell_size=30.0)
euc_dist.save(str(road_proximity_raster))
log(f"Saved road proximity raster to: {road_proximity_raster}")

arcpy.management.CalculateStatistics(str(road_proximity_raster))
dist_max = float(arcpy.management.GetRasterProperties(str(road_proximity_raster), "MAXIMUM").getOutput(0))
dist_mean = float(arcpy.management.GetRasterProperties(str(road_proximity_raster), "MEAN").getOutput(0))
dist_std = float(arcpy.management.GetRasterProperties(str(road_proximity_raster), "STD").getOutput(0))
log(f"Road Distance Statistics: Min=0.00m | Max={dist_max:.2f}m | Mean={dist_mean:.2f}m | StdDev={dist_std:.2f}m")

# Clean temp layers
for temp in [fc_wgs, fc_utm]:
    if arcpy.Exists(temp):
        arcpy.management.Delete(temp)

# Save tables and reports
stats_csv = tables_dir / "road_network_stats.csv"
with open(stats_csv, "w", encoding="utf-8") as f:
    f.write("\n".join(csv_lines))

report_file = logs_dir / "osm_acquisition_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

arcpy.CheckInExtension("Spatial")
log(f"\nOSM processing completed successfully.")
log(f"Table saved to: {stats_csv}")
log(f"Report saved to: {report_file}")
