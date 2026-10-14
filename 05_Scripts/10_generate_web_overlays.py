"""
Script 10: Generate Web-Compatible Transparent PNG Overlays for Leaflet WebGIS
Converts projected analytical GeoTIFFs into georeferenced RGBA PNG overlays:
- Elevation (Terrain colormap)
- Analytical Hillshade (Grayscale)
- Slope (YlOrRd steepness gradient)
- Trafficability Index (4 discrete classes)
- Line-of-Sight Viewshed (High-contrast visibility masked to 5km zone)
- ESA WorldCover 2021 (10m categorical land cover)
Computes exact WGS84 [[south, west], [north, east]] bounds for Leaflet L.imageOverlay.

NOTE: Each raster is read and masked independently to avoid shape broadcast
errors when rasters have slightly different row/column counts due to extent
rounding differences (e.g. 546x692 vs 546x693).
"""
import sys
import os
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import arcpy

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

web_overlays_dir = PROJECT_ROOT / "06_Outputs" / "Web_Overlays"
web_overlays_dir.mkdir(parents=True, exist_ok=True)

# Raster inputs
dem_path = config["dem"]["processed_dem_path"]
hillshade_path = config["terrain_derivatives"]["hillshade_path"]
slope_path = config["terrain_derivatives"]["slope_path"]
landcover_path = PROJECT_ROOT / "03_Processed_Data" / "LandCover" / "worldcover_coonoor_32643.tif"
traffic_class_path = config["trafficability"]["index_raster_classified"]
viewshed_path = config["visibility"]["viewshed_raster"]

print("=" * 60)
print("GENERATING WEB OVERLAYS FOR LEAFLET WEBGIS")
print("=" * 60)

# Get bounding box in WGS84 from the DEM (reference raster)
desc = arcpy.Describe(dem_path)
ext = desc.extent
sr_utm = desc.spatialReference
sr_wgs = arcpy.SpatialReference(4326)

pt_sw = arcpy.PointGeometry(arcpy.Point(ext.XMin, ext.YMin), sr_utm).projectAs(sr_wgs)
pt_ne = arcpy.PointGeometry(arcpy.Point(ext.XMax, ext.YMax), sr_utm).projectAs(sr_wgs)

bounds_wgs84 = [
    [float(pt_sw.firstPoint.Y), float(pt_sw.firstPoint.X)],  # South-West: [Lat, Lon]
    [float(pt_ne.firstPoint.Y), float(pt_ne.firstPoint.X)]   # North-East: [Lat, Lon]
]

print(f"Leaflet Image Overlay Bounds (WGS84 Lat/Lon):")
print(f"  SW: {bounds_wgs84[0]}")
print(f"  NE: {bounds_wgs84[1]}")


def save_rgba_overlay(arr_normalized, cmap, out_path, mask_invalid):
    """Save a normalized array as a transparent RGBA PNG using a matplotlib colormap."""
    rgba = cmap(arr_normalized)  # Returns NxMx4 in range [0, 1]
    rgba[mask_invalid, 3] = 0.0   # Set alpha to 0 for NoData
    rgba_bytes = (rgba * 255).astype(np.uint8)
    img = Image.fromarray(rgba_bytes, mode="RGBA")
    img.save(str(out_path), "PNG", optimize=True)
    print(f"  Saved: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")


def read_raster_with_mask(raster_path, nodata_value=-9999.0, as_int=False):
    """Read a raster to numpy array with its own NoData mask."""
    r = arcpy.Raster(str(raster_path))
    if as_int:
        arr = arcpy.RasterToNumPyArray(r, nodata_to_value=int(nodata_value)).astype(int)
        mask = (arr == int(nodata_value))
    else:
        arr = arcpy.RasterToNumPyArray(r, nodata_to_value=nodata_value).astype(float)
        mask = (arr == nodata_value) | np.isnan(arr)
    return arr, mask


# ─── 1. Elevation Overlay ───────────────────────────────────────────────
print("\n1. Generating Elevation Overlay...")
dem_arr, mask_dem = read_raster_with_mask(dem_path)
valid_dem = dem_arr[~mask_dem]
dem_norm = (dem_arr - valid_dem.min()) / (valid_dem.max() - valid_dem.min())
dem_norm = np.clip(dem_norm, 0, 1)
save_rgba_overlay(dem_norm, plt.cm.terrain, web_overlays_dir / "elevation_overlay.png", mask_dem)

# ─── 2. Hillshade Overlay ───────────────────────────────────────────────
print("2. Generating Hillshade Overlay...")
hs_arr, mask_hs_raw = read_raster_with_mask(hillshade_path, nodata_value=0)
# Also mask where DEM is NoData by aligning shapes
mask_hs = mask_hs_raw.copy()
hs_norm = hs_arr / 255.0
save_rgba_overlay(hs_norm, plt.cm.gray, web_overlays_dir / "hillshade_overlay.png", mask_hs)

# ─── 3. Slope Overlay ───────────────────────────────────────────────────
print("3. Generating Slope Overlay...")
slope_arr, mask_slope = read_raster_with_mask(slope_path)
slope_norm = np.clip(slope_arr / 45.0, 0, 1)  # 0 to 45 degrees
save_rgba_overlay(slope_norm, plt.cm.YlOrRd, web_overlays_dir / "slope_overlay.png", mask_slope)

# ─── 4. Trafficability Classes Overlay (4 discrete colors) ──────────────
print("4. Generating Trafficability Classes Overlay...")
traffic_arr, _ = read_raster_with_mask(traffic_class_path, nodata_value=0, as_int=True)
mask_traffic = (traffic_arr <= 0) | (traffic_arr > 4)

# Colors: 1=#2b83ba (Blue), 2=#abdda4 (Green), 3=#fdae61 (Orange), 4=#d7191c (Red)
h_colors = {
    1: [43, 131, 186, 220],
    2: [171, 221, 164, 220],
    3: [253, 174, 97, 220],
    4: [215, 25, 28, 220]
}
t_rgba = np.zeros((traffic_arr.shape[0], traffic_arr.shape[1], 4), dtype=np.uint8)
for cid, rgba_col in h_colors.items():
    t_rgba[traffic_arr == cid] = rgba_col
t_rgba[mask_traffic, 3] = 0
img_t = Image.fromarray(t_rgba, mode="RGBA")
img_t.save(str(web_overlays_dir / "trafficability_overlay.png"), "PNG", optimize=True)
print(f"  Saved: trafficability_overlay.png ({Path(web_overlays_dir / 'trafficability_overlay.png').stat().st_size / 1024:.1f} KB)")

# ─── 5. Viewshed Overlay (High-contrast Magenta for Visible) ────────────
print("5. Generating Viewshed Overlay...")
vis_arr, _ = read_raster_with_mask(viewshed_path, nodata_value=-9999, as_int=True)
# Build mask for outside-AOI: viewshed raster may have a different extent
mask_vis_nodata = (vis_arr == -9999)

v_rgba = np.zeros((vis_arr.shape[0], vis_arr.shape[1], 4), dtype=np.uint8)
# Visible cells: Bright Magenta / Pink with high opacity
v_rgba[vis_arr > 0] = [255, 0, 128, 230]
# Obscured cells within 5km zone: semi-transparent charcoal
visible_or_obscured = (~mask_vis_nodata) & (vis_arr == 0)
v_rgba[visible_or_obscured] = [40, 40, 40, 90]
v_rgba[mask_vis_nodata, 3] = 0

img_v = Image.fromarray(v_rgba, mode="RGBA")
img_v.save(str(web_overlays_dir / "viewshed_overlay.png"), "PNG", optimize=True)
print(f"  Saved: viewshed_overlay.png ({Path(web_overlays_dir / 'viewshed_overlay.png').stat().st_size / 1024:.1f} KB)")

# ─── 6. ESA WorldCover Overlay ──────────────────────────────────────────
print("6. Generating ESA WorldCover Land Cover Overlay...")
if landcover_path.exists():
    lc_arr, mask_lc = read_raster_with_mask(str(landcover_path), nodata_value=0, as_int=True)

    lc_colors = {
        10: [0, 100, 0, 210],      # Tree cover
        20: [255, 187, 34, 210],   # Shrubland
        30: [255, 255, 76, 210],   # Grassland
        40: [240, 150, 255, 210],  # Cropland (Tea)
        50: [250, 0, 0, 210],      # Built-up
        60: [180, 180, 180, 210],  # Bare
        80: [0, 100, 200, 210]     # Water
    }
    lc_rgba = np.zeros((lc_arr.shape[0], lc_arr.shape[1], 4), dtype=np.uint8)
    for cval, rgba_val in lc_colors.items():
        lc_rgba[lc_arr == cval] = rgba_val
    lc_rgba[mask_lc, 3] = 0
    img_lc = Image.fromarray(lc_rgba, mode="RGBA")
    img_lc.save(str(web_overlays_dir / "landcover_overlay.png"), "PNG", optimize=True)
    print(f"  Saved: landcover_overlay.png ({Path(web_overlays_dir / 'landcover_overlay.png').stat().st_size / 1024:.1f} KB)")
else:
    print("  WARNING: Land cover raster not found, skipping overlay.")

# ─── Save Metadata JSON for WebGIS ──────────────────────────────────────
meta = {
    "crs": "EPSG:32643",
    "wgs84_bounds": bounds_wgs84,
    "center": [
        (bounds_wgs84[0][0] + bounds_wgs84[1][0]) / 2.0,
        (bounds_wgs84[0][1] + bounds_wgs84[1][1]) / 2.0
    ],
    "width_cols": desc.width,
    "height_rows": desc.height,
    "overlays": {
        "elevation": {
            "name": "Digital Elevation Model",
            "file": "elevation_overlay.png",
            "unit": "Meters MSL",
            "min": float(valid_dem.min()),
            "max": float(valid_dem.max())
        },
        "hillshade": {
            "name": "Analytical Hillshade (315°/45°)",
            "file": "hillshade_overlay.png",
            "unit": "Illumination Index (0-255)"
        },
        "slope": {
            "name": "Topographic Slope Steepness",
            "file": "slope_overlay.png",
            "unit": "Degrees",
            "max": 75.78
        },
        "trafficability": {
            "name": "Terrain Trafficability Classification",
            "file": "trafficability_overlay.png",
            "unit": "4-Class Movement Zones"
        },
        "viewshed": {
            "name": "Topographic Viewshed (5km Radius)",
            "file": "viewshed_overlay.png",
            "unit": "Line-of-Sight Visibility"
        },
        "landcover": {
            "name": "ESA WorldCover 2021 Land Cover",
            "file": "landcover_overlay.png",
            "unit": "Categorical Land Cover Classes"
        }
    }
}

meta_path = web_overlays_dir / "web_overlays_metadata.json"
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print(f"\nMetadata saved to: {meta_path}")
print("=" * 60)
print("WEB OVERLAY GENERATION COMPLETE")
print("=" * 60)
