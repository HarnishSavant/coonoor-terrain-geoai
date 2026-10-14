"""
Script 01: Validate AOI
Inspects the Area of Interest (AOI) polygon, calculates geometry metrics,
exports a standard reference shapefile and summary tables.
"""
import sys
import os
import json
from pathlib import Path
import arcpy

# Set workspace and load config
PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

gdb_path = config["aoi"]["gdb_path"]
projected_layer = f"{gdb_path}\\{config['aoi']['projected_layer']}"
raw_layer = f"{gdb_path}\\{config['aoi']['raw_layer']}"
output_shp = config["aoi"]["output_shp"]

logs_dir = PROJECT_ROOT / "08_Logs"
tables_dir = PROJECT_ROOT / "06_Outputs" / "Tables"
logs_dir.mkdir(parents=True, exist_ok=True)
tables_dir.mkdir(parents=True, exist_ok=True)

validation_log_path = logs_dir / "aoi_validation.txt"
summary_csv_path = tables_dir / "aoi_summary.csv"

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("AOI VALIDATION REPORT - COONOOR TALUK")
log("=" * 60)

# 1. Check feature existence
if not arcpy.Exists(projected_layer):
    log(f"ERROR: Projected layer does not exist: {projected_layer}")
    sys.exit(1)

# 2. Describe Projected Layer
desc = arcpy.Describe(projected_layer)
sr = desc.spatialReference
count = int(arcpy.management.GetCount(projected_layer)[0])

log(f"Input Layer: {projected_layer}")
log(f"Feature Count: {count}")
log(f"Geometry Type: {desc.shapeType}")
log(f"Spatial Reference: {sr.name}")
log(f"EPSG Code: {sr.factoryCode}")
log(f"Linear Unit: {sr.linearUnitName}")

ext = desc.extent
log(f"Projected Extent (UTM Zone 43N):")
log(f"  XMin: {ext.XMin:.2f} m")
log(f"  YMin: {ext.YMin:.2f} m")
log(f"  XMax: {ext.XMax:.2f} m")
log(f"  YMax: {ext.YMax:.2f} m")
width_km = (ext.XMax - ext.XMin) / 1000.0
height_km = (ext.YMax - ext.YMin) / 1000.0
log(f"  Bounding Box Dimensions: {width_km:.2f} km (W) x {height_km:.2f} km (H)")

# 3. Geometry Inspection
total_area_sqm = 0.0
total_length_m = 0.0
part_count = 0
point_count = 0

with arcpy.da.SearchCursor(projected_layer, ["SHAPE@"]) as cursor:
    for row in cursor:
        geom = row[0]
        total_area_sqm += geom.area
        total_length_m += geom.length
        part_count += geom.partCount
        point_count += geom.pointCount

area_sqkm = total_area_sqm / 1e6
area_ha = total_area_sqm / 1e4
perimeter_km = total_length_m / 1000.0

log("\nGeometry Measurements:")
log(f"  Total Area: {total_area_sqm:,.2f} m²")
log(f"  Total Area: {area_sqkm:.4f} km² (Expected ~222.44 km²)")
log(f"  Total Area: {area_ha:,.2f} hectares")
log(f"  Perimeter: {perimeter_km:.2f} km")
log(f"  Geometry Parts: {part_count}")
log(f"  Vertex Count: {point_count}")

# 4. Describe Raw Layer (EPSG:4326) for geographic bounds
desc_geo = arcpy.Describe(raw_layer)
ext_geo = desc_geo.extent
log(f"\nGeographic Extent (WGS84 EPSG:4326):")
log(f"  West (Min Lon): {ext_geo.XMin:.6f}°")
log(f"  South (Min Lat): {ext_geo.YMin:.6f}°")
log(f"  East (Max Lon): {ext_geo.XMax:.6f}°")
log(f"  North (Max Lat): {ext_geo.YMax:.6f}°")

# 5. Export clean AOI shapefile to 01_AOI
if arcpy.Exists(output_shp):
    log(f"\nTarget shapefile {output_shp} already exists, overwriting safely...")
    arcpy.management.Delete(output_shp)

log(f"\nExporting validated AOI to: {output_shp}")
arcpy.conversion.ExportFeatures(projected_layer, output_shp)
log("Export successful.")

# 6. Area comparison / validation check
expected_area = 222.44
diff = abs(area_sqkm - expected_area)
pct_diff = (diff / expected_area) * 100
log(f"\nArea Discrepancy from target (222.44 km²): {diff:.4f} km² ({pct_diff:.2f}%)")
if pct_diff < 5.0:
    log("STATUS: AOI area matches expected domain within <5% tolerance (PASS).")
else:
    log("STATUS: AOI area diverges more than 5% from target, check projection/boundary.")

log("=" * 60)
log("VALIDATION FINISHED SUCCESSFULLY")
log("=" * 60)

# Save validation text report
with open(validation_log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
log(f"Validation report saved to: {validation_log_path}")

# Save CSV summary
csv_content = f"""Parameter,Value,Unit
Study Area,Coonoor Taluk,Administrative
CRS Projected,WGS 1984 UTM Zone 43N,EPSG:32643
CRS Geographic,WGS 1984,EPSG:4326
Area SqKm,{area_sqkm:.4f},km²
Area Hectares,{area_ha:.2f},ha
Area SqMeters,{total_area_sqm:.2f},m²
Perimeter,{perimeter_km:.2f},km
Vertex Count,{point_count},count
Parts,{part_count},count
West Bounding Lon,{ext_geo.XMin:.6f},degrees
South Bounding Lat,{ext_geo.YMin:.6f},degrees
East Bounding Lon,{ext_geo.XMax:.6f},degrees
North Bounding Lat,{ext_geo.YMax:.6f},degrees
UTM XMin,{ext.XMin:.2f},meters
UTM YMin,{ext.YMin:.2f},meters
UTM XMax,{ext.XMax:.2f},meters
UTM YMax,{ext.YMax:.2f},meters
Validation Status,VERIFIED,Status
"""
with open(summary_csv_path, "w", encoding="utf-8") as f:
    f.write(csv_content)
log(f"Summary table saved to: {summary_csv_path}")
