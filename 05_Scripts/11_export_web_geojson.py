"""
Script 11: Export vector layers as WGS84 GeoJSON for Leaflet WebGIS
Converts UTM Zone 43N shapefiles to WGS84 (EPSG:4326) GeoJSON.
"""
import json
from pathlib import Path
import arcpy

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
web_dir = PROJECT_ROOT / "06_Outputs" / "Web_App" / "data"
web_dir.mkdir(parents=True, exist_ok=True)

sr_wgs = arcpy.SpatialReference(4326)

# 1. Export AOI boundary
print("Exporting AOI boundary to WGS84 GeoJSON...")
aoi_shp = str(PROJECT_ROOT / "01_AOI" / "coonoor_aoi_utm.shp")
aoi_out = str(web_dir / "coonoor_aoi.geojson")
arcpy.management.Project(aoi_shp, str(web_dir / "temp_aoi_wgs84.shp"), sr_wgs)
arcpy.conversion.FeaturesToJSON(
    str(web_dir / "temp_aoi_wgs84.shp"), aoi_out, geoJSON="GEOJSON"
)
# Clean temp
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    f = web_dir / f"temp_aoi_wgs84{ext}"
    if f.exists():
        f.unlink()
print(f"  Saved: {aoi_out}")

# 2. Export roads (simplified)
print("Exporting OSM roads to WGS84 GeoJSON...")
roads_shp = str(PROJECT_ROOT / "03_Processed_Data" / "OSM" / "coonoor_roads_utm.shp")
roads_out = str(web_dir / "coonoor_roads.geojson")
arcpy.management.Project(roads_shp, str(web_dir / "temp_roads_wgs84.shp"), sr_wgs)
arcpy.conversion.FeaturesToJSON(
    str(web_dir / "temp_roads_wgs84.shp"), roads_out, geoJSON="GEOJSON"
)
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    f = web_dir / f"temp_roads_wgs84{ext}"
    if f.exists():
        f.unlink()
print(f"  Saved: {roads_out}")

# 3. Export observer point
print("Exporting observer point to WGS84 GeoJSON...")
obs_shp = str(PROJECT_ROOT / "03_Processed_Data" / "Visibility" / "observer_points.shp")
obs_out = str(web_dir / "observer_point.geojson")
arcpy.management.Project(obs_shp, str(web_dir / "temp_obs_wgs84.shp"), sr_wgs)
arcpy.conversion.FeaturesToJSON(
    str(web_dir / "temp_obs_wgs84.shp"), obs_out, geoJSON="GEOJSON"
)
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    f = web_dir / f"temp_obs_wgs84{ext}"
    if f.exists():
        f.unlink()
print(f"  Saved: {obs_out}")

print("\nAll vector exports complete.")
