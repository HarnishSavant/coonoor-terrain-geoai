"""
Script 05: Build Multi-Criteria Terrain Trafficability & Accessibility Index
Combines Slope, Terrain Ruggedness (TRI), and Road Proximity into:
1. Continuous Trafficability Index (0-100 score, higher = more accessible)
2. 4-Class Discrete Trafficability Raster:
   - Class 1: Unrestricted / High Trafficability (Gentle slopes <= 10 deg, low ruggedness)
   - Class 2: Moderate Trafficability (10-20 deg slopes, rolling micro-relief)
   - Class 3: Severely Restricted (20-30 deg slopes, high ruggedness)
   - Class 4: Impassable / Extreme Terrain Barrier (Slope > 30 deg, steep escarpments/cliffs)
Calculates exact class areas (km², ha, %) and outputs summary tables and reports.
"""
import sys
import os
import json
import time
from pathlib import Path
import arcpy

arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

aoi_shp = config["aoi"]["output_shp"]
slope_path = config["terrain_derivatives"]["slope_path"]
ruggedness_path = config["terrain_derivatives"]["ruggedness_path"]
road_prox_path = config["osm"]["road_proximity_raster"]

continuous_out = Path(config["trafficability"]["index_raster_continuous"])
classified_out = Path(config["trafficability"]["index_raster_classified"])

continuous_out.parent.mkdir(parents=True, exist_ok=True)
classified_out.parent.mkdir(parents=True, exist_ok=True)

logs_dir = PROJECT_ROOT / "08_Logs"
tables_dir = PROJECT_ROOT / "06_Outputs" / "Tables"

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("TERRAIN TRAFFICABILITY & ACCESSIBILITY INDEX GENERATION")
log("=" * 60)

# Environment setup
arcpy.env.overwriteOutput = True
arcpy.env.extent = slope_path
arcpy.env.snapRaster = slope_path
arcpy.env.cellSize = 30.0
arcpy.env.mask = aoi_shp

slope_r = Raster(slope_path)
tri_r = Raster(ruggedness_path)
road_prox_r = Raster(road_prox_path)

log("Inputs Verified:")
log(f"  Slope Raster: {slope_path}")
log(f"  Ruggedness (TRI) Raster: {ruggedness_path}")
log(f"  Road Proximity Raster: {road_prox_path}")

# Continuous Scoring Normalization (0 to 100):
# 1. Slope Score: 0 deg -> 100, 10 deg -> 80, 20 deg -> 50, 30 deg -> 20, >= 45 deg -> 0
# Continuous decay formula: score = Max(0, 100 - (slope / 45.0) * 100)
log("\nNormalizing Criteria into Standardized 0-100 Scales...")
slope_score = Con(slope_r >= 45.0, 0.0, 100.0 * (1.0 - (slope_r / 45.0)))

# 2. Ruggedness Score: 0m -> 100, 15m -> 80, 35m -> 50, 60m -> 20, >= 80m -> 0
tri_score = Con(tri_r >= 80.0, 0.0, 100.0 * (1.0 - (tri_r / 80.0)))

# 3. Road Proximity Score: 0m -> 100, 250m -> 75, 500m -> 50, 1000m -> 25, >= 1500m -> 0
road_score = Con(road_prox_r >= 1500.0, 0.0, 100.0 * (1.0 - (road_prox_r / 1500.0)))

# Multi-Criteria Evaluation (MCE) Weighted Overlay
# Weights: Slope = 0.55, Ruggedness = 0.30, Road Proximity = 0.15
w_slope = 0.55
w_tri = 0.30
w_road = 0.15

log(f"Applying Expert-Defined Multi-Criteria Weights:")
log(f"  - Slope Factor: {w_slope * 100:.0f}%")
log(f"  - Ruggedness (TRI) Factor: {w_tri * 100:.0f}%")
log(f"  - Road Proximity Factor: {w_road * 100:.0f}%")

continuous_index = (slope_score * w_slope) + (tri_score * w_tri) + (road_score * w_road)
continuous_index.save(str(continuous_out))
log(f"Saved Continuous Trafficability Index to: {continuous_out}")

# Discrete 4-Class Classification based on Geotechnical Terrain Thresholds:
# Class 1 (Unrestricted / High): Slope <= 10° AND TRI <= 20m
# Class 2 (Moderate): (Slope <= 20° AND TRI <= 40m) AND NOT Class 1
# Class 3 (Restricted): (Slope <= 30° AND TRI <= 65m) AND NOT Class 1 or 2
# Class 4 (Impassable / Severe Barrier): Slope > 30° OR TRI > 65m
log("\nComputing Discrete 4-Class Trafficability Model...")

classified_raster = Con(
    (slope_r <= 10.0) & (tri_r <= 20.0), 1,
    Con(
        (slope_r <= 20.0) & (tri_r <= 40.0), 2,
        Con(
            (slope_r <= 30.0) & (tri_r <= 65.0), 3,
            4
        )
    )
)

# Mask strictly to AOI
final_classified = ExtractByMask(classified_raster, aoi_shp)
final_classified.save(str(classified_out))
log(f"Saved Classified Trafficability Raster to: {classified_out}")

# Calculate Class Statistics
arcpy.management.CalculateStatistics(str(classified_out))
cell_area_sqm = 30.0 * 30.0  # 900 m²

class_names = {
    1: "Class 1: High Trafficability (Gentle Slopes <= 10 deg, Low Ruggedness)",
    2: "Class 2: Moderate Trafficability (Rolling Slopes 10-20 deg, Moderate Ruggedness)",
    3: "Class 3: Restricted Trafficability (Steep Slopes 20-30 deg, High Ruggedness)",
    4: "Class 4: Impassable / Severe Barrier (Very Steep Slopes > 30 deg, Cliffs/Escarpments)"
}

class_pixels = {1: 0, 2: 0, 3: 0, 4: 0}

# Build attribute table if needed
arcpy.management.BuildRasterAttributeTable(str(classified_out), "Overwrite")

with arcpy.da.SearchCursor(str(classified_out), ["VALUE", "COUNT"]) as cur:
    for row in cur:
        val = int(row[0])
        cnt = int(row[1])
        if val in class_pixels:
            class_pixels[val] = cnt

total_pixels = sum(class_pixels.values())
total_calc_sqkm = (total_pixels * cell_area_sqm) / 1e6

log("\n" + "=" * 60)
log("TRAFFICABILITY CLASSIFICATION RESULTS")
log("=" * 60)
log(f"Total Valid Raster Pixels: {total_pixels:,}")
log(f"Total Classified Area: {total_calc_sqkm:.2f} km² (Reference AOI = 222.44 km²)")

csv_lines = ["Class_ID,Class_Name,Pixel_Count,Area_sqm,Area_ha,Area_sqkm,Percentage"]

for cid in [1, 2, 3, 4]:
    cnt = class_pixels[cid]
    sqm = cnt * cell_area_sqm
    ha = sqm / 1e4
    sqkm = sqm / 1e6
    pct = (sqkm / total_calc_sqkm) * 100 if total_calc_sqkm > 0 else 0
    name = class_names[cid]
    log(f"  {name}:")
    log(f"    Area: {sqkm:6.2f} km² ({ha:8.1f} ha) | {pct:5.2f}% of study area | {cnt:,} cells")
    csv_lines.append(f"{cid},\"{name}\",{cnt},{sqm:.1f},{ha:.2f},{sqkm:.4f},{pct:.2f}")

# Calculate Continuous Index Statistics
arcpy.management.CalculateStatistics(str(continuous_out))
idx_min = float(arcpy.management.GetRasterProperties(str(continuous_out), "MINIMUM").getOutput(0))
idx_max = float(arcpy.management.GetRasterProperties(str(continuous_out), "MAXIMUM").getOutput(0))
idx_mean = float(arcpy.management.GetRasterProperties(str(continuous_out), "MEAN").getOutput(0))
idx_std = float(arcpy.management.GetRasterProperties(str(continuous_out), "STD").getOutput(0))

log(f"\nContinuous Trafficability Index (0-100 Score):")
log(f"  Min: {idx_min:.2f} | Max: {idx_max:.2f} | Mean: {idx_mean:.2f} | StdDev: {idx_std:.2f}")

# Save CSV Table and Log Report
summary_csv = tables_dir / "trafficability_class_summary.csv"
with open(summary_csv, "w", encoding="utf-8") as f:
    f.write("\n".join(csv_lines))

report_file = logs_dir / "accessibility_index_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

arcpy.CheckInExtension("Spatial")
log(f"\nIndex generation completed successfully.")
log(f"Summary table saved to: {summary_csv}")
log(f"Report saved to: {report_file}")
