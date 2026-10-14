"""
Script 03: Process Terrain Derivatives
Generates standard geomorphometric derivatives using ArcPy Spatial Analyst:
- Elevation (m)
- Slope (degrees and percent rise)
- Aspect (compass degrees)
- Hillshade (azimuth 315, altitude 45)
- Curvature (standard topographic surface curvature)
- Ruggedness (Local Elevation Range / TRI 3x3)
All outputs strictly aligned to EPSG:32643 and 30.0m cell size.
"""
import sys
import os
import json
import time
from pathlib import Path
import arcpy

# Spatial Analyst check out
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

processed_dem_path = config["dem"]["processed_dem_path"]
aoi_shp = config["aoi"]["output_shp"]

terrain_dir = PROJECT_ROOT / "03_Processed_Data" / "Terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)
logs_dir = PROJECT_ROOT / "08_Logs"
tables_dir = PROJECT_ROOT / "06_Outputs" / "Tables"

log_lines = []
stats_records = []

def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("TERRAIN DERIVATIVES PROCESSING - COONOOR TALUK")
log("=" * 60)

if not arcpy.Exists(processed_dem_path):
    log(f"ERROR: Base DEM does not exist: {processed_dem_path}")
    sys.exit(1)

arcpy.env.overwriteOutput = True
arcpy.env.extent = processed_dem_path
arcpy.env.snapRaster = processed_dem_path
arcpy.env.cellSize = 30.0
arcpy.env.mask = aoi_shp

dem_raster = Raster(processed_dem_path)
log(f"Base Elevation Raster: {processed_dem_path}")

# 1. Elevation raster in Terrain folder
elevation_out = terrain_dir / "elevation.tif"
if not elevation_out.exists():
    log(f"Saving baseline elevation to: {elevation_out}")
    dem_raster.save(str(elevation_out))

# 2. Slope (Degrees)
slope_deg_out = terrain_dir / "slope_deg.tif"
log(f"\nComputing Slope (Degrees)...")
t0 = time.time()
slope_deg = Slope(dem_raster, "DEGREE", 1.0)
slope_deg.save(str(slope_deg_out))
log(f"  Saved slope_deg.tif in {time.time() - t0:.1f}s")

# 3. Slope (Percent Rise)
slope_pct_out = terrain_dir / "slope_pct.tif"
log(f"\nComputing Slope (Percent Rise)...")
t0 = time.time()
slope_pct = Slope(dem_raster, "PERCENT_RISE", 1.0)
slope_pct.save(str(slope_pct_out))
log(f"  Saved slope_pct.tif in {time.time() - t0:.1f}s")

# 4. Aspect
aspect_out = terrain_dir / "aspect.tif"
log(f"\nComputing Aspect...")
t0 = time.time()
aspect = Aspect(dem_raster)
aspect.save(str(aspect_out))
log(f"  Saved aspect.tif in {time.time() - t0:.1f}s")

# 5. Hillshade (Azimuth 315, Altitude 45)
hillshade_out = terrain_dir / "hillshade.tif"
log(f"\nComputing Analytical Hillshade (Azimuth=315, Altitude=45)...")
t0 = time.time()
hillshade = Hillshade(dem_raster, azimuth=315, altitude=45)
hillshade.save(str(hillshade_out))
log(f"  Saved hillshade.tif in {time.time() - t0:.1f}s")

# 6. Curvature
curvature_out = terrain_dir / "curvature.tif"
log(f"\nComputing Topographic Curvature...")
t0 = time.time()
curvature = Curvature(dem_raster)
curvature.save(str(curvature_out))
log(f"  Saved curvature.tif in {time.time() - t0:.1f}s")

# 7. Ruggedness Index (Terrain Ruggedness Index / Local Elevation Range 3x3)
ruggedness_out = terrain_dir / "tri_ruggedness.tif"
log(f"\nComputing Terrain Ruggedness Index (3x3 focal elevation range)...")
t0 = time.time()
ruggedness = FocalStatistics(dem_raster, NbrRectangle(3, 3, "CELL"), "RANGE")
ruggedness.save(str(ruggedness_out))
log(f"  Saved tri_ruggedness.tif in {time.time() - t0:.1f}s")

# Calculate and record statistics for each derivative
derivatives = [
    ("Elevation", elevation_out, "Meters"),
    ("Slope_Degrees", slope_deg_out, "Degrees"),
    ("Slope_Percent", slope_pct_out, "Percent"),
    ("Aspect", aspect_out, "Compass Degrees"),
    ("Hillshade", hillshade_out, "Illumination (0-255)"),
    ("Curvature", curvature_out, "1/100 z-units"),
    ("Ruggedness_TRI", ruggedness_out, "Elevation Range (m)")
]

log("\n" + "=" * 60)
log("TERRAIN METRICS SUMMARY")
log("=" * 60)

stats_csv_lines = ["Metric,Path,Units,Min,Max,Mean,StdDev,CellSize_m,CRS"]

for name, path, units in derivatives:
    arcpy.management.CalculateStatistics(str(path))
    r_min = float(arcpy.management.GetRasterProperties(str(path), "MINIMUM").getOutput(0))
    r_max = float(arcpy.management.GetRasterProperties(str(path), "MAXIMUM").getOutput(0))
    r_mean = float(arcpy.management.GetRasterProperties(str(path), "MEAN").getOutput(0))
    r_std = float(arcpy.management.GetRasterProperties(str(path), "STD").getOutput(0))
    desc = arcpy.Describe(str(path))
    
    log(f"{name:16}: Min={r_min:8.2f} | Max={r_max:8.2f} | Mean={r_mean:8.2f} | Std={r_std:8.2f} {units}")
    stats_csv_lines.append(f"{name},{path.name},{units},{r_min:.2f},{r_max:.2f},{r_mean:.2f},{r_std:.2f},30.0,EPSG:32643")

report_file = logs_dir / "terrain_derivatives_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

stats_csv_file = tables_dir / "terrain_stats.csv"
with open(stats_csv_file, "w", encoding="utf-8") as f:
    f.write("\n".join(stats_csv_lines))

arcpy.CheckInExtension("Spatial")
log(f"\nProcessing completed successfully.")
log(f"Report saved to: {report_file}")
log(f"Statistics table saved to: {stats_csv_file}")
