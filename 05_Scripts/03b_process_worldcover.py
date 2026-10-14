"""
Script 03b: Acquire and Process ESA WorldCover 2021 (10m Land Cover)
Source: ESA WorldCover v200 (2021) 10m Global Land Cover (AWS Open Data)
Target CRS: WGS 1984 UTM Zone 43N (EPSG:32643)
Resolution: 30.0m (Nearest-neighbor resampled to preserve discrete categorical classes)
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
raw_lc_dir = PROJECT_ROOT / "02_Raw_Data" / "WorldCover"
proc_lc_dir = PROJECT_ROOT / "03_Processed_Data" / "LandCover"
tables_dir = PROJECT_ROOT / "06_Outputs" / "Tables"
logs_dir = PROJECT_ROOT / "08_Logs"

raw_lc_dir.mkdir(parents=True, exist_ok=True)
proc_lc_dir.mkdir(parents=True, exist_ok=True)
tables_dir.mkdir(parents=True, exist_ok=True)
logs_dir.mkdir(parents=True, exist_ok=True)

worldcover_url = "https://esa-worldcover.s3.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N09E075_Map.tif"
raw_lc_path = raw_lc_dir / "ESA_WorldCover_10m_2021_v200_N09E075_Map.tif"
proc_lc_path = proc_lc_dir / "worldcover_coonoor_32643.tif"

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("ESA WORLDCOVER 2021 ACQUISITION & PROCESSING - COONOOR TALUK")
log("=" * 60)

# Step 1: Download raw tile if not present
if raw_lc_path.exists() and raw_lc_path.stat().st_size > 10 * 1024 * 1024:
    log(f"Raw WorldCover tile already exists: {raw_lc_path} ({raw_lc_path.stat().st_size / (1024**2):.1f} MB)")
else:
    log(f"Downloading ESA WorldCover 2021 tile from:\n  {worldcover_url}")
    t0 = time.time()
    resp = requests.get(worldcover_url, stream=True, timeout=60)
    resp.raise_for_status()
    total_bytes = int(resp.headers.get("content-length", 0))
    
    downloaded = 0
    with open(raw_lc_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_bytes > 0:
                    pct = (downloaded / total_bytes) * 100
                    print(f"  Progress: {pct:.1f}% ({downloaded / (1024**2):.1f} MB)", end="\r")
    log(f"\nDownload completed in {time.time() - t0:.1f}s. Saved to: {raw_lc_path}")

# Step 2: Reproject and Clip to AOI (NEAREST Neighbor for Categorical Data)
log("\nReprojecting & Clipping Land Cover to EPSG:32643 (Cell Size: 30m, NEAREST)...")
temp_projected = str(proc_lc_dir / "temp_projected_lc.tif")
arcpy.env.overwriteOutput = True

target_sr = arcpy.SpatialReference(32643)
arcpy.management.ProjectRaster(
    in_raster=str(raw_lc_path),
    out_raster=temp_projected,
    out_coor_system=target_sr,
    resampling_type="NEAREST",
    cell_size="30.0 30.0"
)
log("  ProjectRaster completed.")

# Clip to AOI mask
extracted_lc = ExtractByMask(temp_projected, aoi_shp)
extracted_lc.save(str(proc_lc_path))
log(f"  Clipped Land Cover saved to: {proc_lc_path}")

if arcpy.Exists(temp_projected):
    arcpy.management.Delete(temp_projected)

# Step 3: Compute Class Distribution
arcpy.management.CalculateStatistics(str(proc_lc_path))
arcpy.management.BuildRasterAttributeTable(str(proc_lc_path), "Overwrite")

# ESA WorldCover Legend Mapping
class_meta = {
    10: ("Tree cover", "#006400"),
    20: ("Shrubland", "#ffbb22"),
    30: ("Grassland", "#ffff4c"),
    40: ("Cropland (Tea/Coffee Estates)", "#f096ff"),
    50: ("Built-up (Settlements/Urban)", "#fa0000"),
    60: ("Bare / sparse vegetation", "#b4b4b4"),
    70: ("Snow and ice", "#f0f0f0"),
    80: ("Permanent water bodies", "#0064c8"),
    90: ("Herbaceous wetland", "#0096a0"),
    95: ("Mangroves", "#00cf75"),
    100: ("Moss and lichen", "#fae6a0")
}

cell_area_sqm = 30.0 * 30.0
class_counts = {}
with arcpy.da.SearchCursor(str(proc_lc_path), ["VALUE", "COUNT"]) as cur:
    for row in cur:
        val = int(row[0])
        cnt = int(row[1])
        class_counts[val] = cnt

total_cells = sum(class_counts.values())
total_sqkm = (total_cells * cell_area_sqm) / 1e6

log("\n" + "=" * 60)
log("ESA WORLDCOVER LAND COVER DISTRIBUTION - COONOOR TALUK")
log("=" * 60)
log(f"Total Valid Raster Pixels: {total_cells:,} ({total_sqkm:.2f} km²)")

csv_lines = ["Class_Value,Class_Name,Hex_Color,Pixel_Count,Area_sqkm,Area_ha,Percentage"]

for val in sorted(class_counts.keys()):
    cnt = class_counts[val]
    sqm = cnt * cell_area_sqm
    ha = sqm / 1e4
    sqkm = sqm / 1e6
    pct = (sqkm / total_sqkm) * 100 if total_sqkm > 0 else 0
    cname, color = class_meta.get(val, ("Other", "#333333"))
    log(f"  Class {val:2d} ({cname:28}): {sqkm:6.2f} km² ({ha:7.1f} ha) | {pct:5.2f}%")
    csv_lines.append(f"{val},\"{cname}\",{color},{cnt},{sqkm:.4f},{ha:.2f},{pct:.2f}")

stats_csv = tables_dir / "landcover_stats.csv"
with open(stats_csv, "w", encoding="utf-8") as f:
    f.write("\n".join(csv_lines))

report_file = logs_dir / "landcover_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

arcpy.CheckInExtension("Spatial")
log(f"\nLand cover processing completed successfully.")
log(f"Table saved to: {stats_csv}")
log(f"Report saved to: {report_file}")
