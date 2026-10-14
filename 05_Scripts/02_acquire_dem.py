"""
Script 02: Acquire and Prepare Digital Elevation Model (DEM)
Source: Copernicus GLO-30 Public Dataset (ESA / Airbus via AWS Open Data)
Target CRS: WGS 1984 UTM Zone 43N (EPSG:32643)
Resolution: 30.0 meters
"""
import sys
import os
import json
import time
from pathlib import Path
import requests
import arcpy

# Check out Spatial Analyst
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

dem_url = config["dem"]["dem_url"]
raw_dem_path = Path(config["dem"]["raw_dem_path"])
processed_dem_path = Path(config["dem"]["processed_dem_path"])
aoi_shp = config["aoi"]["output_shp"]

raw_dem_path.parent.mkdir(parents=True, exist_ok=True)
processed_dem_path.parent.mkdir(parents=True, exist_ok=True)

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("DEM ACQUISITION & PREPARATION - COONOOR TALUK")
log("=" * 60)

# Step 1: Download raw DEM if not already present
if raw_dem_path.exists() and raw_dem_path.stat().st_size > 10 * 1024 * 1024:
    log(f"Raw DEM already present: {raw_dem_path} ({raw_dem_path.stat().st_size / (1024**2):.2f} MB)")
else:
    log(f"Downloading Copernicus GLO-30 tile from:\n  {dem_url}")
    t0 = time.time()
    resp = requests.get(dem_url, stream=True, timeout=60)
    resp.raise_for_status()
    total_bytes = int(resp.headers.get("content-length", 0))
    log(f"Download size: {total_bytes / (1024**2):.2f} MB")
    
    downloaded = 0
    with open(raw_dem_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_bytes > 0:
                    pct = (downloaded / total_bytes) * 100
                    print(f"  Progress: {pct:.1f}% ({downloaded / (1024**2):.1f} MB)", end="\r")
    log(f"\nDownload completed in {time.time() - t0:.1f} seconds. Saved to: {raw_dem_path}")

# Step 2: Validate raw DEM raster
log("\nValidating Raw DEM Raster:")
if not arcpy.Exists(str(raw_dem_path)):
    log(f"ERROR: Cannot open raw DEM with ArcPy: {raw_dem_path}")
    sys.exit(1)

desc_raw = arcpy.Describe(str(raw_dem_path))
sr_raw = desc_raw.spatialReference
ext_raw = desc_raw.extent
log(f"  Format: {desc_raw.format}")
log(f"  CRS: {sr_raw.name} (EPSG:{sr_raw.factoryCode})")
log(f"  Cell Size: {desc_raw.meanCellWidth:.6f} x {desc_raw.meanCellHeight:.6f} deg (~30 m)")
log(f"  Raw Bounds: XMin={ext_raw.XMin:.2f}, YMin={ext_raw.YMin:.2f}, XMax={ext_raw.XMax:.2f}, YMax={ext_raw.YMax:.2f}")

# Step 3: Reproject and Clip to AOI (UTM Zone 43N)
log("\nReprojecting and Clipping DEM to Study Area (EPSG:32643)...")
arcpy.env.overwriteOutput = True
target_sr = arcpy.SpatialReference(32643)
target_res = float(config["dem"]["target_resolution_m"])

# Temporary reprojected raster
temp_projected = str(PROJECT_ROOT / "03_Processed_Data" / "DEM" / "temp_projected_dem.tif")

log(f"  Projecting raster to UTM Zone 43N (Bilinear interpolation, cell size = {target_res}m)...")
arcpy.management.ProjectRaster(
    in_raster=str(raw_dem_path),
    out_raster=temp_projected,
    out_coor_system=target_sr,
    resampling_type="BILINEAR",
    cell_size=f"{target_res} {target_res}"
)
log("  ProjectRaster completed.")

# Clip to AOI boundary with extraction mask
log(f"  Extracting by Mask using AOI: {aoi_shp}...")
arcpy.env.snapRaster = temp_projected
extracted_dem = ExtractByMask(temp_projected, aoi_shp)
extracted_dem.save(str(processed_dem_path))
log(f"  Clipped DEM successfully saved to: {processed_dem_path}")

# Clean up temporary reprojected raster
if arcpy.Exists(temp_projected):
    arcpy.management.Delete(temp_projected)

# Step 4: Validate Processed DEM
log("\nValidating Processed DEM:")
desc_proc = arcpy.Describe(str(processed_dem_path))
sr_proc = desc_proc.spatialReference
ext_proc = desc_proc.extent

# Calculate statistics
arcpy.management.CalculateStatistics(str(processed_dem_path))
dem_min = float(arcpy.management.GetRasterProperties(str(processed_dem_path), "MINIMUM").getOutput(0))
dem_max = float(arcpy.management.GetRasterProperties(str(processed_dem_path), "MAXIMUM").getOutput(0))
dem_mean = float(arcpy.management.GetRasterProperties(str(processed_dem_path), "MEAN").getOutput(0))
dem_std = float(arcpy.management.GetRasterProperties(str(processed_dem_path), "STD").getOutput(0))

log(f"  Spatial Reference: {sr_proc.name} (EPSG:{sr_proc.factoryCode})")
log(f"  Cell Size: {desc_proc.meanCellWidth:.2f} m x {desc_proc.meanCellHeight:.2f} m")
log(f"  Raster Columns: {desc_proc.width}, Rows: {desc_proc.height}")
log(f"  Elevation Min: {dem_min:.2f} m")
log(f"  Elevation Max: {dem_max:.2f} m")
log(f"  Elevation Mean: {dem_mean:.2f} m")
log(f"  Elevation StdDev: {dem_std:.2f} m")

# Realistic elevation check for Coonoor / Nilgiris
if 200 <= dem_min <= 1000 and 1800 <= dem_max <= 2700:
    log("  STATUS: Elevation range is completely consistent with Nilgiris/Coonoor terrain (PASS).")
else:
    log(f"  WARNING: Elevation range [{dem_min:.1f}, {dem_max:.1f}] differs from standard Nilgiris expectations.")

# Write report to log
report_path = PROJECT_ROOT / "08_Logs" / "dem_acquisition_report.txt"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

arcpy.CheckInExtension("Spatial")
log(f"\nDEM Acquisition & Processing Complete. Log saved to: {report_path}")
