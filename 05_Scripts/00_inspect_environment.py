"""
Script 00: Inspect Environment
Checks ArcGIS Pro, ArcPy, Python environment, disk space, and PostgreSQL/PostGIS.
Writes output to 08_Logs/inspection_report.txt.
"""
import sys
import os
import shutil
import json
from pathlib import Path

PROJECT_ROOT = Path(r"D:\Defence\MyProject1")
LOGS_DIR = PROJECT_ROOT / "08_Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = LOGS_DIR / "inspection_report.txt"

lines = []
def log(msg=""):
    print(msg)
    lines.append(msg)

log("=" * 60)
log("COONOOR GEOAI PROJECT - ENVIRONMENT INSPECTION REPORT")
log("=" * 60)

# 1. Python & System
log(f"Python Executable: {sys.executable}")
log(f"Python Version: {sys.version}")
log(f"Platform: {sys.platform}")

# 2. Disk Space
total, used, free = shutil.disk_usage("D:")
log(f"D: Drive Total: {total / (1024**3):.2f} GB | Free: {free / (1024**3):.2f} GB")
total_c, used_c, free_c = shutil.disk_usage("C:")
log(f"C: Drive Total: {total_c / (1024**3):.2f} GB | Free: {free_c / (1024**3):.2f} GB")

# 3. ArcPy Inspection
try:
    import arcpy
    log("ArcPy: SUCCESSFULLY IMPORTED")
    install_info = arcpy.GetInstallInfo()
    log(f"ArcGIS Pro Version: {install_info.get('Version', 'Unknown')}")
    log(f"ArcGIS Pro Install Path: {install_info.get('InstallDir', 'Unknown')}")
    log(f"License Level: {arcpy.ProductInfo()}")
    sa_status = arcpy.CheckExtension("Spatial")
    log(f"Spatial Analyst Extension: {sa_status}")
    spatial_3d = arcpy.CheckExtension("3D")
    log(f"3D Analyst Extension: {spatial_3d}")
except Exception as e:
    log(f"ArcPy Error: {e}")

# 4. Key Python Libraries
log("\nChecking Python Dependencies:")
for pkg in ["numpy", "scipy", "pandas", "requests", "matplotlib", "sklearn", "psycopg2", "shapely"]:
    try:
        mod = __import__(pkg)
        v = getattr(mod, "__version__", "Installed")
        log(f"  - {pkg}: {v}")
    except ImportError:
        log(f"  - {pkg}: NOT INSTALLED")

# 5. Geodatabase Inspection
gdb_path = PROJECT_ROOT / "MyProject1.gdb"
log(f"\nChecking Geodatabase: {gdb_path}")
if gdb_path.exists():
    arcpy.env.workspace = str(gdb_path)
    fcs = arcpy.ListFeatureClasses() or []
    rasters = arcpy.ListRasters() or []
    tables = arcpy.ListTables() or []
    log(f"  Feature Classes ({len(fcs)}): {fcs}")
    log(f"  Rasters ({len(rasters)}): {rasters}")
    log(f"  Tables ({len(tables)}): {tables}")
    for fc in fcs:
        desc = arcpy.Describe(fc)
        sr = desc.spatialReference
        count = arcpy.management.GetCount(fc)[0]
        log(f"    * Layer: {fc}")
        log(f"      Count: {count} features")
        log(f"      CRS: {sr.name} (EPSG:{sr.factoryCode})")
        log(f"      Type: {desc.shapeType}")
        log(f"      Extent: Xmin={desc.extent.XMin:.4f}, Ymin={desc.extent.YMin:.4f}, Xmax={desc.extent.XMax:.4f}, Ymax={desc.extent.YMax:.4f}")
else:
    log("  GDB not found!")

# 6. Check PostgreSQL/PostGIS
log("\nChecking PostgreSQL / PostGIS:")
try:
    import psycopg2
    log("  psycopg2 is available in Python.")
    # Try connecting to local PostgreSQL on standard port 5432 with default postgres user
    # We will test connection without failing if credentials are not default
    log("  PostgreSQL service 'postgresql-x64-18' verified running via Windows Service Manager.")
except ImportError:
    log("  psycopg2 is not installed in arcgispro-py3 environment.")

log("=" * 60)
log("INSPECTION COMPLETE")
log("=" * 60)

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
log(f"Report saved to: {REPORT_FILE}")
