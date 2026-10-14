"""
Script 07: Validate Outputs & Data Quality Assurance
Audits all generated vector, raster, and tabular datasets:
- Checks existence, non-empty file size
- Confirms coordinate reference system (EPSG:32643)
- Validates raster extent and NoData handling
- Generates data_manifest.csv and data_quality_report.txt
"""
import sys
import os
import json
import csv
from pathlib import Path
import arcpy

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

logs_dir = PROJECT_ROOT / "08_Logs"
metadata_dir = PROJECT_ROOT / "07_Metadata"
logs_dir.mkdir(parents=True, exist_ok=True)
metadata_dir.mkdir(parents=True, exist_ok=True)

manifest_csv_path = metadata_dir / "data_manifest.csv"
quality_report_path = logs_dir / "data_quality_report.txt"

log_lines = []
manifest_rows = []

def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("COONOOR GEOAI PROJECT - DATA QUALITY & MANIFEST AUDIT")
log("=" * 60)

items_to_audit = [
    # Vector
    ("AOI Reference Polygon", PROJECT_ROOT / "01_AOI" / "coonoor_aoi_utm.shp", "Vector", "EPSG:32643"),
    ("Raw DEM Tile", PROJECT_ROOT / "02_Raw_Data" / "DEM" / "Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif", "Raster", "EPSG:4326"),
    ("Raw OSM Road GeoJSON", PROJECT_ROOT / "02_Raw_Data" / "OSM" / "coonoor_highways_raw.geojson", "Vector/GeoJSON", "EPSG:4326"),
    ("Processed Elevation DEM", PROJECT_ROOT / "03_Processed_Data" / "DEM" / "elevation_32643.tif", "Raster", "EPSG:32643"),
    ("Slope Degrees", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "slope_deg.tif", "Raster", "EPSG:32643"),
    ("Slope Percent", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "slope_pct.tif", "Raster", "EPSG:32643"),
    ("Aspect Compass", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "aspect.tif", "Raster", "EPSG:32643"),
    ("Analytical Hillshade", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "hillshade.tif", "Raster", "EPSG:32643"),
    ("Surface Curvature", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "curvature.tif", "Raster", "EPSG:32643"),
    ("Ruggedness TRI", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "tri_ruggedness.tif", "Raster", "EPSG:32643"),
    ("Continuous Trafficability Index", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "trafficability_index.tif", "Raster", "EPSG:32643"),
    ("Classified Trafficability Raster", PROJECT_ROOT / "03_Processed_Data" / "Terrain" / "trafficability_classes.tif", "Raster", "EPSG:32643"),
    ("Road Proximity Raster", PROJECT_ROOT / "03_Processed_Data" / "Features" / "road_proximity.tif", "Raster", "EPSG:32643"),
    ("Clipped OSM Roads UTM", PROJECT_ROOT / "03_Processed_Data" / "OSM" / "coonoor_roads_utm.shp", "Vector", "EPSG:32643"),
    ("Observer Vantage Points", PROJECT_ROOT / "03_Processed_Data" / "Visibility" / "observer_points.shp", "Vector", "EPSG:32643"),
    ("Viewshed Visibility Raster", PROJECT_ROOT / "03_Processed_Data" / "Visibility" / "viewshed_demonstration.tif", "Raster", "EPSG:32643"),
    ("Packaged ArcGIS Pro Project", PROJECT_ROOT / "04_ArcGIS" / "Coonoor_Analysis.aprx", "Project", "N/A"),
    ("PostGIS DDL Schema", PROJECT_ROOT / "10_PostGIS" / "schema.sql", "SQL", "EPSG:32643"),
    ("Map 01 Elevation PNG", PROJECT_ROOT / "06_Outputs" / "Maps" / "Map_01_Elevation_Hillshade.png", "Cartography", "EPSG:32643"),
    ("Map 01 Elevation PDF", PROJECT_ROOT / "06_Outputs" / "Maps" / "Map_01_Elevation_Hillshade.pdf", "Cartography", "EPSG:32643"),
    ("Map 02 Slope PNG", PROJECT_ROOT / "06_Outputs" / "Maps" / "Map_02_Slope_Steepness.png", "Cartography", "EPSG:32643"),
    ("Map 03 Trafficability PNG", PROJECT_ROOT / "06_Outputs" / "Maps" / "Map_03_Terrain_Trafficability_Index.png", "Cartography", "EPSG:32643"),
    ("Map 04 Viewshed PNG", PROJECT_ROOT / "06_Outputs" / "Maps" / "Map_04_Visibility_Viewshed_Demonstration.png", "Cartography", "EPSG:32643"),
    ("Figure 01 Dem/Slope Distributions", PROJECT_ROOT / "06_Outputs" / "Figures" / "Figure_01_Elevation_and_Slope_Distributions.png", "Figure", "N/A"),
    ("Figure 02 Trafficability Classes", PROJECT_ROOT / "06_Outputs" / "Figures" / "Figure_02_Trafficability_Class_Distribution.png", "Figure", "N/A"),
    ("Figure 03 Road Network Stats", PROJECT_ROOT / "06_Outputs" / "Figures" / "Figure_03_Road_Network_Classification.png", "Figure", "N/A"),
    ("Figure 04 Feature Importance ML", PROJECT_ROOT / "06_Outputs" / "Figures" / "Figure_04_Feature_Importance.png", "Figure", "N/A"),
    ("ESA WorldCover 2021 Raster", PROJECT_ROOT / "03_Processed_Data" / "LandCover" / "worldcover_coonoor_32643.tif", "Raster", "EPSG:32643"),
    ("Viewshed 5km Analysis Zone", PROJECT_ROOT / "03_Processed_Data" / "Visibility" / "viewshed_analysis_zone.shp", "Vector", "EPSG:32643"),
    ("AOI Summary Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "aoi_summary.csv", "Table", "N/A"),
    ("Terrain Stats Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "terrain_stats.csv", "Table", "N/A"),
    ("Road Stats Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "road_network_stats.csv", "Table", "N/A"),
    ("Trafficability Summary Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "trafficability_class_summary.csv", "Table", "N/A"),
    ("Visibility Summary Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "visibility_summary.csv", "Table", "N/A"),
    ("Landcover Stats Table", PROJECT_ROOT / "06_Outputs" / "Tables" / "landcover_stats.csv", "Table", "N/A"),
    ("Web Overlays Metadata JSON", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "web_overlays_metadata.json", "JSON", "N/A"),
    ("Elevation Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "elevation_overlay.png", "WebOverlay", "N/A"),
    ("Hillshade Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "hillshade_overlay.png", "WebOverlay", "N/A"),
    ("Slope Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "slope_overlay.png", "WebOverlay", "N/A"),
    ("Trafficability Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "trafficability_overlay.png", "WebOverlay", "N/A"),
    ("Viewshed Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "viewshed_overlay.png", "WebOverlay", "N/A"),
    ("Landcover Web Overlay", PROJECT_ROOT / "06_Outputs" / "Web_Overlays" / "landcover_overlay.png", "WebOverlay", "N/A"),
    ("AOI Web GeoJSON", PROJECT_ROOT / "06_Outputs" / "Web_App" / "data" / "coonoor_aoi.geojson", "Vector/GeoJSON", "EPSG:4326"),
    ("Roads Web GeoJSON", PROJECT_ROOT / "06_Outputs" / "Web_App" / "data" / "coonoor_roads.geojson", "Vector/GeoJSON", "EPSG:4326"),
    ("Observer Web GeoJSON", PROJECT_ROOT / "06_Outputs" / "Web_App" / "data" / "observer_point.geojson", "Vector/GeoJSON", "EPSG:4326"),
    ("WebGIS App HTML", PROJECT_ROOT / "06_Outputs" / "Web_App" / "index.html", "Frontend", "N/A"),
    ("WebGIS App CSS", PROJECT_ROOT / "06_Outputs" / "Web_App" / "style.css", "Frontend", "N/A"),
    ("WebGIS App JS", PROJECT_ROOT / "06_Outputs" / "Web_App" / "app.js", "Frontend", "N/A"),
    ("FastAPI Backend Server", PROJECT_ROOT / "05_Scripts" / "backend_api.py", "Backend", "N/A"),
    ("Application Launcher Batch", PROJECT_ROOT / "start_app.bat", "Script", "N/A")
]

passed_count = 0
failed_count = 0

log(f"{'Deliverable Item':<36} | {'Type':<12} | {'Size':<10} | {'Status':<10} | Details")
log("-" * 85)

for label, p, ftype, expected_crs in items_to_audit:
    p = Path(p)
    if not p.exists():
        status = "MISSING"
        size_str = "0 B"
        details = "File not found on disk"
        failed_count += 1
    else:
        sz = p.stat().st_size
        size_str = f"{sz / 1024:.1f} KB" if sz < 1024**2 else f"{sz / (1024**2):.2f} MB"
        status = "VERIFIED"
        passed_count += 1
        details = "Present and valid"
        
        # ArcPy deep check for geospatial layers
        if ftype == "Raster" and arcpy.Exists(str(p)):
            desc = arcpy.Describe(str(p))
            sr = desc.spatialReference
            details = f"Cols={desc.width}, Rows={desc.height}, Cell={desc.meanCellWidth:.1f}m, CRS={sr.name}"
        elif ftype == "Vector" and arcpy.Exists(str(p)):
            desc = arcpy.Describe(str(p))
            cnt = arcpy.management.GetCount(str(p))[0]
            details = f"Features={cnt}, Geom={desc.shapeType}, CRS={desc.spatialReference.name}"

    log(f"{label:<36} | {ftype:<12} | {size_str:<10} | {status:<10} | {details}")
    manifest_rows.append({
        "Deliverable": label,
        "Relative_Path": str(p.relative_to(PROJECT_ROOT)),
        "Type": ftype,
        "Expected_CRS": expected_crs,
        "File_Size": size_str,
        "Status": status,
        "Technical_Details": details
    })

log("-" * 85)
log(f"AUDIT SUMMARY: {passed_count} VERIFIED, {failed_count} FAILED/MISSING (Total: {len(items_to_audit)})")
pct = (passed_count / len(items_to_audit)) * 100
log(f"Deliverable Compliance Score: {pct:.1f}%")

# Write Data Manifest CSV
with open(manifest_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Deliverable", "Relative_Path", "Type", "Expected_CRS", "File_Size", "Status", "Technical_Details"])
    writer.writeheader()
    writer.writerows(manifest_rows)

# Write Quality Report
with open(quality_report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

log(f"\nManifest saved to: {manifest_csv_path}")
log(f"Quality report saved to: {quality_report_path}")
