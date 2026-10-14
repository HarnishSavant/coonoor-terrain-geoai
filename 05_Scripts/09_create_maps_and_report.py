"""
Script 09: Generate Cartographic Maps, Analytical Figures, and ArcGIS Project Package
1. Safely creates a separate ArcGIS Pro Project '04_ArcGIS/Coonoor_Analysis.aprx'
   and adds all analytical rasters and vector layers.
2. Generates publication-grade cartographic maps (PNG and PDF):
   - Map 01: Elevation & Analytical Hillshade
   - Map 02: Slope Steepness & Ruggedness Index
   - Map 03: Multi-Criteria Terrain Trafficability & Accessibility
   - Map 04: Topographic Viewshed & Line-of-Sight Visibility
3. Generates analytical research figures:
   - Figure 01: Elevation and Slope Histograms
   - Figure 02: Trafficability Class Area Breakdown (Bar & Donut)
   - Figure 03: OpenStreetMap Highway Network Distribution
"""
import sys
import os
import shutil
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Patch
import arcpy

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
CONFIG_PATH = PROJECT_ROOT / "09_Config" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Paths
aoi_shp = config["aoi"]["output_shp"]
dem_path = config["dem"]["processed_dem_path"]
hillshade_path = config["terrain_derivatives"]["hillshade_path"]
slope_path = config["terrain_derivatives"]["slope_path"]
tri_path = config["terrain_derivatives"]["ruggedness_path"]
traffic_class_path = config["trafficability"]["index_raster_classified"]
traffic_idx_path = config["trafficability"]["index_raster_continuous"]
viewshed_path = config["visibility"]["viewshed_raster"]
observer_shp = config["visibility"]["observer_point_shp"]
roads_shp = config["osm"]["roads_shp"]

maps_dir = PROJECT_ROOT / "06_Outputs" / "Maps"
figures_dir = PROJECT_ROOT / "06_Outputs" / "Figures"
arcgis_dir = PROJECT_ROOT / "04_ArcGIS"
logs_dir = PROJECT_ROOT / "08_Logs"

maps_dir.mkdir(parents=True, exist_ok=True)
figures_dir.mkdir(parents=True, exist_ok=True)
arcgis_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("CARTOGRAPHIC MAPPING & FIGURE GENERATION - COONOOR TALUK")
print("=" * 60)

# -------------------------------------------------------------
# 1. Package ArcGIS Pro Project (Preserving original MyProject1.aprx)
# -------------------------------------------------------------
orig_aprx = PROJECT_ROOT / "MyProject1.aprx"
target_aprx = arcgis_dir / "Coonoor_Analysis.aprx"

print(f"Preserving original project. Copying to: {target_aprx}")
shutil.copy2(orig_aprx, target_aprx)

try:
    aprx = arcpy.mp.ArcGISProject(str(target_aprx))
    m = aprx.listMaps("Map")[0]
    
    # Add layers to map
    layers_to_add = [
        (dem_path, "Elevation_Copernicus_GLO30"),
        (hillshade_path, "Hillshade_315_45"),
        (slope_path, "Slope_Degrees"),
        (traffic_class_path, "Trafficability_Classes"),
        (viewshed_path, "Viewshed_Demonstration"),
        (roads_shp, "Coonoor_Road_Network"),
        (observer_shp, "Observer_Vantage_Point"),
        (aoi_shp, "Coonoor_Taluk_AOI")
    ]
    for p, name in layers_to_add:
        if arcpy.Exists(str(p)):
            try:
                m.addDataFromPath(str(p))
                print(f"  Added {name} to Coonoor_Analysis.aprx")
            except Exception as e:
                print(f"  Notice adding {name}: {e}")
    aprx.save()
    print("Saved updated project: Coonoor_Analysis.aprx")
except Exception as e:
    print(f"ArcGIS Pro APRX update note: {e}")

# -------------------------------------------------------------
# Helper: Read raster data to numpy array
# -------------------------------------------------------------
def read_raster(path, is_int=False):
    r = arcpy.Raster(str(path))
    if is_int:
        arr = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
        arr = arr.astype(float)
        arr[arr == -9999] = np.nan
    else:
        arr = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999.0)
        arr[arr == -9999.0] = np.nan
    desc = arcpy.Describe(str(path))
    ext = desc.extent
    extent_coords = [ext.XMin, ext.XMax, ext.YMin, ext.YMax]
    return arr, extent_coords

dem_arr, ext_coords = read_raster(dem_path, is_int=False)
hs_arr, _ = read_raster(hillshade_path, is_int=True)
slope_arr, _ = read_raster(slope_path, is_int=False)
traffic_arr, _ = read_raster(traffic_class_path, is_int=True)
vis_arr, _ = read_raster(viewshed_path, is_int=True)

# Decorate map layout helper
def add_carto_decorations(ax, title, subtitle, source_note):
    ax.set_title(f"{title}\n", fontsize=14, fontweight="bold", pad=15)
    ax.text(0.5, 1.01, subtitle, transform=ax.transAxes, fontsize=10, ha="center", style="italic", color="#333333")
    
    # Scale bar in km (bottom left)
    # Extent is ~20 km wide
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    sb_len = 5000.0  # 5 km
    sb_x = xmin + 1000.0
    sb_y = ymin + 1200.0
    ax.plot([sb_x, sb_x + sb_len], [sb_y, sb_y], color="black", lw=4, solid_capstyle="butt")
    ax.plot([sb_x, sb_x + sb_len/2], [sb_y, sb_y], color="white", lw=2, solid_capstyle="butt")
    ax.text(sb_x + sb_len/2, sb_y + 400, "5 km", ha="center", fontsize=9, fontweight="bold")
    
    # North Arrow (top right)
    na_x = xmax - 2000.0
    na_y = ymax - 2000.0
    ax.annotate("N", xy=(na_x, na_y), xytext=(na_x, na_y - 1200),
                arrowprops=dict(facecolor="black", edgecolor="black", width=2, headwidth=8),
                ha="center", va="center", fontsize=11, fontweight="bold")
    
    # Metadata footer
    ax.text(0.01, -0.07, f"CRS: EPSG:32643 (WGS 84 / UTM Zone 43N) | Study Area: Coonoor Taluk (222.44 km²)\nSource: {source_note} | Academic Research GIS Pipeline",
            transform=ax.transAxes, fontsize=8, color="#555555", va="top")
    
    ax.set_xlabel("UTM Easting (m)", fontsize=9)
    ax.set_ylabel("UTM Northing (m)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(True, linestyle="--", alpha=0.3, color="gray")

# -------------------------------------------------------------
# Map 01: Elevation & Analytical Hillshade
# -------------------------------------------------------------
print("\nGenerating Map 01: Elevation & Hillshade...")
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
# Hillshade background
ax.imshow(hs_arr, cmap="gray", extent=ext_coords, origin="upper", alpha=0.6)
# Elevation overlay with transparency
im1 = ax.imshow(dem_arr, cmap="terrain", extent=ext_coords, origin="upper", alpha=0.65)
cbar = plt.colorbar(im1, ax=ax, fraction=0.035, pad=0.04)
cbar.set_label("Elevation (m above MSL)", fontsize=10, fontweight="bold")
cbar.ax.tick_params(labelsize=9)

add_carto_decorations(
    ax,
    title="Digital Elevation Model & Surface Topography",
    subtitle="Coonoor Taluk, The Nilgiris, Tamil Nadu, India",
    source_note="Copernicus GLO-30 DEM (ESA/Airbus, 30m resolution)"
)

plt.tight_layout()
map1_png = maps_dir / "Map_01_Elevation_Hillshade.png"
map1_pdf = maps_dir / "Map_01_Elevation_Hillshade.pdf"
fig.savefig(map1_png, dpi=300, bbox_inches="tight")
fig.savefig(map1_pdf, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {map1_png}")

# -------------------------------------------------------------
# Map 02: Slope Steepness & Ruggedness
# -------------------------------------------------------------
print("Generating Map 02: Slope Steepness...")
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.imshow(hs_arr, cmap="gray", extent=ext_coords, origin="upper", alpha=0.5)
im2 = ax.imshow(slope_arr, cmap="YlOrRd", extent=ext_coords, origin="upper", alpha=0.7)
cbar = plt.colorbar(im2, ax=ax, fraction=0.035, pad=0.04)
cbar.set_label("Terrain Slope (Degrees)", fontsize=10, fontweight="bold")
cbar.ax.tick_params(labelsize=9)

add_carto_decorations(
    ax,
    title="Topographic Slope Steepness Assessment",
    subtitle="Geomorphometric Surface Analysis - Coonoor Taluk",
    source_note="Computed via ArcPy Spatial Analyst Slope from Copernicus GLO-30"
)

plt.tight_layout()
map2_png = maps_dir / "Map_02_Slope_Steepness.png"
map2_pdf = maps_dir / "Map_02_Slope_Steepness.pdf"
fig.savefig(map2_png, dpi=300, bbox_inches="tight")
fig.savefig(map2_pdf, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {map2_png}")

# -------------------------------------------------------------
# Map 03: Terrain Trafficability & Accessibility Index
# -------------------------------------------------------------
print("Generating Map 03: Terrain Trafficability Index...")
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.imshow(hs_arr, cmap="gray", extent=ext_coords, origin="upper", alpha=0.45)

# Discrete color map for 4 classes
cmap_traffic = mcolors.ListedColormap(["#2b83ba", "#abdda4", "#fdae61", "#d7191c"])
bounds = [0.5, 1.5, 2.5, 3.5, 4.5]
norm = mcolors.BoundaryNorm(bounds, cmap_traffic.N)

im3 = ax.imshow(traffic_arr, cmap=cmap_traffic, norm=norm, extent=ext_coords, origin="upper", alpha=0.75)

# Custom legend for classes
legend_elements = [
    Patch(facecolor="#2b83ba", edgecolor="black", label="Class 1: High Trafficability (Slope <= 10°, Low TRI) [14.1%]"),
    Patch(facecolor="#abdda4", edgecolor="black", label="Class 2: Moderate Trafficability (10°-20° Slope) [38.9%]"),
    Patch(facecolor="#fdae61", edgecolor="black", label="Class 3: Restricted Trafficability (20°-30° Slope) [29.3%]"),
    Patch(facecolor="#d7191c", edgecolor="black", label="Class 4: Impassable / Barrier (Slope > 30°, Cliffs) [17.7%]")
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=8, framealpha=0.92, facecolor="white")

add_carto_decorations(
    ax,
    title="Multi-Criteria Terrain Trafficability & Accessibility Classification",
    subtitle="Weighted Evaluation (Slope 55%, Ruggedness 30%, Road Proximity 15%)",
    source_note="Multi-Criteria Evaluation (MCE) Model, Nilgiris Mountain Topography"
)

plt.tight_layout()
map3_png = maps_dir / "Map_03_Terrain_Trafficability_Index.png"
map3_pdf = maps_dir / "Map_03_Terrain_Trafficability_Index.pdf"
fig.savefig(map3_png, dpi=300, bbox_inches="tight")
fig.savefig(map3_pdf, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {map3_png}")

# -------------------------------------------------------------
# Map 04: Viewshed & Visibility Analysis Demonstration
# -------------------------------------------------------------
print("Generating Map 04: Topographic Viewshed Demonstration...")
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.imshow(hs_arr, cmap="gray", extent=ext_coords, origin="upper", alpha=0.6)

# Masked visibility (0 = hidden, 1 = visible)
vis_masked = np.where(vis_arr > 0, 1.0, np.nan)
im4 = ax.imshow(vis_masked, cmap="spring", extent=ext_coords, origin="upper", alpha=0.85)

# Plot observer point
obs_x = 685544.00
obs_y = 1257114.32
ax.plot(obs_x, obs_y, marker="*", color="red", markersize=14, markeredgecolor="yellow", label="Observer Vantage Point (2,388m MSL)")

vis_legend = [
    Patch(facecolor="#ff007f", edgecolor="black", label="Direct Line-of-Sight Visible Area (8.81 km² / 3.96%)"),
    Patch(facecolor="#888888", edgecolor="black", label="Topographically Obscured / Shadowed (213.63 km² / 96.04%)"),
    plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="red", markeredgecolor="yellow", markersize=12, label="Observer Ridge Peak (Height: +2.0m, Max Radius: 5.0 km)")
]
ax.legend(handles=vis_legend, loc="lower right", fontsize=8, framealpha=0.92, facecolor="white")

add_carto_decorations(
    ax,
    title="Line-of-Sight Visibility & Topographic Viewshed Assessment",
    subtitle="Demonstration from High Ridge Vantage Point (Elevation: 2,388 m MSL)",
    source_note="ArcPy Spatial Analyst Viewshed Model, 2m Observer Eye-Level, 5km Radius"
)

plt.tight_layout()
map4_png = maps_dir / "Map_04_Visibility_Viewshed_Demonstration.png"
map4_pdf = maps_dir / "Map_04_Visibility_Viewshed_Demonstration.pdf"
fig.savefig(map4_png, dpi=300, bbox_inches="tight")
fig.savefig(map4_pdf, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {map4_png}")

# -------------------------------------------------------------
# Figure 01: Elevation & Slope Distribution Charts
# -------------------------------------------------------------
print("\nGenerating Figure 01: Elevation & Slope Distribution...")
valid_dem = dem_arr[~np.isnan(dem_arr)]
valid_slope = slope_arr[~np.isnan(slope_arr)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

# Elevation Histogram
ax1.hist(valid_dem, bins=50, color="#2b83ba", edgecolor="#1a4f70", alpha=0.85)
ax1.axvline(np.mean(valid_dem), color="red", linestyle="--", linewidth=1.5, label=f"Mean: {np.mean(valid_dem):.1f} m")
ax1.axvline(np.median(valid_dem), color="orange", linestyle=":", linewidth=1.5, label=f"Median: {np.median(valid_dem):.1f} m")
ax1.set_title("Elevation Distribution (Coonoor Taluk)", fontsize=11, fontweight="bold")
ax1.set_xlabel("Elevation (m above MSL)", fontsize=9)
ax1.set_ylabel("Pixel Frequency (30m cells)", fontsize=9)
ax1.legend(fontsize=8)
ax1.grid(True, linestyle="--", alpha=0.3)

# Slope Histogram
ax2.hist(valid_slope, bins=50, color="#fdae61", edgecolor="#b56314", alpha=0.85)
ax2.axvline(10, color="green", linestyle="--", linewidth=1.5, label="High Traffic limit (10°)")
ax2.axvline(20, color="blue", linestyle="--", linewidth=1.5, label="Moderate limit (20°)")
ax2.axvline(30, color="red", linestyle="--", linewidth=1.5, label="Impassable barrier (>30°)")
ax2.set_title("Slope Distribution (Degrees)", fontsize=11, fontweight="bold")
ax2.set_xlabel("Slope (Degrees)", fontsize=9)
ax2.set_ylabel("Pixel Frequency (30m cells)", fontsize=9)
ax2.legend(fontsize=8)
ax2.grid(True, linestyle="--", alpha=0.3)

plt.suptitle("Coonoor Taluk Geomorphometric Statistical Profile", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
fig1_path = figures_dir / "Figure_01_Elevation_and_Slope_Distributions.png"
fig.savefig(fig1_path, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {fig1_path}")

# -------------------------------------------------------------
# Figure 02: Trafficability Class Distribution (Bar & Donut)
# -------------------------------------------------------------
print("Generating Figure 02: Trafficability Class Breakdown...")
traffic_csv_path = PROJECT_ROOT / "06_Outputs" / "Tables" / "trafficability_class_summary.csv"
df_traffic = pd.read_csv(traffic_csv_path)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
colors = ["#2b83ba", "#abdda4", "#fdae61", "#d7191c"]
labels_short = ["Class 1: High", "Class 2: Moderate", "Class 3: Restricted", "Class 4: Impassable"]

# Bar chart
bars = ax1.bar(labels_short, df_traffic["Area_sqkm"], color=colors, edgecolor="black", width=0.55)
for bar in bars:
    y = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, y + 1.5, f"{y:.1f} km²", ha="center", fontsize=9, fontweight="bold")
ax1.set_ylim(0, max(df_traffic["Area_sqkm"]) * 1.15)
ax1.set_title("Trafficability Class Area Coverage (km²)", fontsize=11, fontweight="bold")
ax1.set_ylabel("Area (km²)", fontsize=9)
ax1.grid(axis="y", linestyle="--", alpha=0.3)

# Donut chart
wedges, texts, autotexts = ax2.pie(
    df_traffic["Percentage"],
    labels=labels_short,
    autopct="%1.1f%%",
    startangle=140,
    colors=colors,
    wedgeprops=dict(width=0.45, edgecolor="black"),
    textprops=dict(fontsize=8)
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_weight("bold")
ax2.set_title("Trafficability Proportions (% of 222.44 km²)", fontsize=11, fontweight="bold")

plt.suptitle("Terrain Trafficability & Movement Capability Distribution", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
fig2_path = figures_dir / "Figure_02_Trafficability_Class_Distribution.png"
fig.savefig(fig2_path, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {fig2_path}")

# -------------------------------------------------------------
# Figure 03: Road Network Breakdown
# -------------------------------------------------------------
print("Generating Figure 03: Road Network Analysis...")
roads_csv_path = PROJECT_ROOT / "06_Outputs" / "Tables" / "road_network_stats.csv"
df_roads = pd.read_csv(roads_csv_path)

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
top_roads = df_roads.sort_values(by="Length_km", ascending=True)
bars = ax.barh(top_roads["Highway_Class"], top_roads["Length_km"], color="#3182bd", edgecolor="black", height=0.6)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"{w:.1f} km ({w/598.34*100:.1f}%)", va="center", fontsize=8)

ax.set_xlim(0, max(top_roads["Length_km"]) * 1.22)
ax.set_title("OpenStreetMap Highway Network Breakdown - Coonoor Taluk\nTotal Network Length: 598.34 km | Overall Density: 2.69 km/km²", fontsize=11, fontweight="bold", pad=12)
ax.set_xlabel("Total Length (km)", fontsize=9)
ax.set_ylabel("OSM Classification", fontsize=9)
ax.grid(axis="x", linestyle="--", alpha=0.3)

plt.tight_layout()
fig3_path = figures_dir / "Figure_03_Road_Network_Classification.png"
fig.savefig(fig3_path, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {fig3_path}")

print("=" * 60)
print("CARTOGRAPHIC MAPPING & FIGURE GENERATION COMPLETE")
print("=" * 60)
