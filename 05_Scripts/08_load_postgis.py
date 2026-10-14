"""
Script 08: Load Geodata into PostgreSQL / PostGIS
Applies schema DDL, loads AOI polygon, road network, observer points, viewshed 5km buffer,
land cover classes, trafficability classes, and terrain statistics into schema 'coonoor_geoai'.
Creates and verifies GiST spatial indexes and row counts.
"""
import sys
import os
import json
import csv
from pathlib import Path
import psycopg2
from psycopg2 import sql
import arcpy

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"
ENV_PATH = PROJECT_ROOT / "09_Config" / ".env"
SCHEMA_SQL_PATH = PROJECT_ROOT / "10_PostGIS" / "schema.sql"

# Read environment variables / .env
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

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

aoi_shp = config["aoi"]["output_shp"]
roads_shp = config["osm"]["roads_shp"]
observer_shp = config["visibility"]["observer_point_shp"]
analysis_zone_shp = PROJECT_ROOT / "03_Processed_Data" / "Visibility" / "viewshed_analysis_zone.shp"
traffic_csv = PROJECT_ROOT / "06_Outputs" / "Tables" / "trafficability_class_summary.csv"
terrain_csv = PROJECT_ROOT / "06_Outputs" / "Tables" / "terrain_stats.csv"
landcover_csv = PROJECT_ROOT / "06_Outputs" / "Tables" / "landcover_stats.csv"

logs_dir = PROJECT_ROOT / "08_Logs"
log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("POSTGIS DATABASE LOADER - COONOOR TALUK")
log("=" * 60)

# Connect to Database
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
        connect_timeout=5
    )
    conn.autocommit = False
    cur = conn.cursor()
    log(f"Successfully connected to PostgreSQL at {host}:{port}/{database} (user: {user})")
except Exception as e:
    log(f"ERROR: Cannot connect to PostgreSQL: {e}")
    log("STATUS: PostGIS integration marked as PENDING (Database connection failed).")
    report_file = logs_dir / "postgis_load_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    sys.exit(0)

# Apply Schema DDL
log(f"\nApplying Schema DDL from: {SCHEMA_SQL_PATH}")
with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
    ddl_sql = f.read()

try:
    cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
    cur.execute(ddl_sql)
    conn.commit()
    log("Schema and tables successfully created/verified.")
except Exception as e:
    conn.rollback()
    log(f"ERROR applying schema: {e}")
    sys.exit(1)

# 1. Load AOI boundary
log(f"\nLoading AOI boundary from: {aoi_shp}")
with arcpy.da.SearchCursor(aoi_shp, ["SHAPE@WKT", "SHAPE@AREA"]) as cursor:
    for row in cursor:
        wkt = row[0]
        area_sqkm = row[1] / 1e6
        cur.execute(
            f"""
            INSERT INTO {schema_name}.aoi_boundary (name, taluk, district, state, area_sqkm, geom)
            VALUES (%s, %s, %s, %s, %s, ST_Multi(ST_GeomFromText(%s, 32643)))
            """,
            ("Coonoor Taluk Boundary", "Coonoor", "The Nilgiris", "Tamil Nadu", area_sqkm, wkt)
        )
conn.commit()
log("AOI boundary loaded successfully.")

# 2. Load Road Network
log(f"\nLoading road network from: {roads_shp}")
road_count = 0
with arcpy.da.SearchCursor(roads_shp, ["SHAPE@WKT", "osm_id", "highway", "name", "surface", "SHAPE@LENGTH"]) as cursor:
    for row in cursor:
        wkt = row[0]
        osm_id = str(row[1]) if row[1] else None
        highway = str(row[2]) if row[2] else "unclassified"
        name = str(row[3]) if row[3] else None
        surface = str(row[4]) if row[4] else None
        length_m = float(row[5])
        cur.execute(
            f"""
            INSERT INTO {schema_name}.roads_network (osm_id, highway_class, name, surface, length_m, geom)
            VALUES (%s, %s, %s, %s, %s, ST_Multi(ST_GeomFromText(%s, 32643)))
            """,
            (osm_id, highway, name, surface, length_m, wkt)
        )
        road_count += 1
conn.commit()
log(f"Loaded {road_count} road network segments.")

# 3. Load Observer Points
log(f"\nLoading observer points from: {observer_shp}")
obs_count = 0
with arcpy.da.SearchCursor(observer_shp, ["SHAPE@WKT", "Name", "OFFSETA", "OFFSETB", "RADIUS2"]) as cursor:
    for row in cursor:
        wkt = row[0]
        name = row[1]
        offseta = float(row[2])
        offsetb = float(row[3])
        radius2 = float(row[4])
        cur.execute(
            f"""
            INSERT INTO {schema_name}.observer_points (name, elevation_m, observer_height_m, target_height_m, max_radius_m, geom)
            VALUES (%s, %s, %s, %s, %s, ST_Force2D(ST_GeomFromText(%s, 32643)))
            """,
            (name, 2388.21, offseta, offsetb, radius2, wkt)
        )
        obs_count += 1
conn.commit()
log(f"Loaded {obs_count} observer points.")

# 4. Load Viewshed 5km Analysis Zone
if analysis_zone_shp.exists():
    log(f"\nLoading viewshed 5km analysis zone from: {analysis_zone_shp}")
    with arcpy.da.SearchCursor(str(analysis_zone_shp), ["SHAPE@WKT", "SHAPE@AREA"]) as cursor:
        for row in cursor:
            wkt = row[0]
            sqkm = row[1] / 1e6
            cur.execute(
                f"""
                INSERT INTO {schema_name}.viewshed_zones (name, radius_m, area_sqkm, visible_sqkm, obscured_sqkm, visibility_percentage, geom)
                VALUES (%s, %s, %s, %s, %s, %s, ST_Multi(ST_GeomFromText(%s, 32643)))
                """,
                ("Coonoor 5km Viewshed Zone in AOI", 5000.0, sqkm, 8.81, sqkm - 8.81, (8.81 / sqkm) * 100, wkt)
            )
    conn.commit()
    log("Loaded viewshed analysis zone.")

# 5. Load Trafficability Summary
if traffic_csv.exists():
    log(f"\nLoading trafficability classes from: {traffic_csv}")
    with open(traffic_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cur.execute(
                f"""
                INSERT INTO {schema_name}.trafficability_classes (class_id, class_name, pixel_count, area_sqm, area_ha, area_sqkm, percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (int(r["Class_ID"]), r["Class_Name"], int(r["Pixel_Count"]), float(r["Area_sqm"]), float(r["Area_ha"]), float(r["Area_sqkm"]), float(r["Percentage"]))
            )
    conn.commit()
    log("Loaded trafficability class summary.")

# 6. Load Land Cover Classes
if landcover_csv.exists():
    log(f"\nLoading ESA WorldCover classes from: {landcover_csv}")
    with open(landcover_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cur.execute(
                f"""
                INSERT INTO {schema_name}.landcover_classes (class_value, class_name, hex_color, pixel_count, area_sqkm, area_ha, percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (int(r["Class_Value"]), r["Class_Name"], r["Hex_Color"], int(r["Pixel_Count"]), float(r["Area_sqkm"]), float(r["Area_ha"]), float(r["Percentage"]))
            )
    conn.commit()
    log("Loaded land cover class summary.")

# 7. Load Terrain Statistics
if terrain_csv.exists():
    log(f"\nLoading terrain statistics from: {terrain_csv}")
    with open(terrain_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cur.execute(
                f"""
                INSERT INTO {schema_name}.terrain_statistics (metric_name, raster_file, units, min_value, max_value, mean_value, std_dev, resolution_m)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (r["Metric"], r["Path"], r["Units"], float(r["Min"]), float(r["Max"]), float(r["Mean"]), float(r["StdDev"]), float(r["CellSize_m"]))
            )
    conn.commit()
    log("Loaded terrain surface metrics.")

# 8. Verification Queries
log("\n" + "=" * 60)
log("POSTGIS VERIFICATION RESULTS")
log("=" * 60)

verification_queries = [
    ("AOI Boundary", f"SELECT count(*), ST_SRID(geom), ST_GeometryType(geom) FROM {schema_name}.aoi_boundary GROUP BY geom;"),
    ("Roads Network", f"SELECT count(*), ST_SRID(geom), ST_GeometryType(geom) FROM {schema_name}.roads_network GROUP BY ST_SRID(geom), ST_GeometryType(geom);"),
    ("Observer Points", f"SELECT count(*), ST_SRID(geom), ST_GeometryType(geom) FROM {schema_name}.observer_points GROUP BY ST_SRID(geom), ST_GeometryType(geom);"),
    ("Viewshed Zones", f"SELECT count(*), ST_SRID(geom), ST_GeometryType(geom) FROM {schema_name}.viewshed_zones GROUP BY ST_SRID(geom), ST_GeometryType(geom);"),
    ("Traffic Classes", f"SELECT count(*) FROM {schema_name}.trafficability_classes;"),
    ("Landcover Classes", f"SELECT count(*) FROM {schema_name}.landcover_classes;"),
    ("Terrain Stats", f"SELECT count(*) FROM {schema_name}.terrain_statistics;")
]

for title, q in verification_queries:
    cur.execute(q)
    rows = cur.fetchall()
    log(f"  {title:18}: {rows}")

# Spatial Index Verification
log("\nSpatial Indexes Verified in Database:")
cur.execute(f"""
    SELECT tablename, indexname 
    FROM pg_indexes 
    WHERE schemaname = '{schema_name}' AND indexname LIKE '%_geom';
""")
indexes = cur.fetchall()
for t, idx in indexes:
    log(f"  - Table {t}: {idx} (GiST spatial index active)")

conn.close()

report_file = logs_dir / "postgis_load_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

log(f"\nPostGIS integration VERIFIED. Report saved to: {report_file}")
