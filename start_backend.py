"""
Launcher for Coonoor GeoAI FastAPI Backend & WebGIS Service.
Run with: python start_backend.py
"""
import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = PROJECT_ROOT / "05_Scripts" / "backend_api.py"

python_candidates = [
    Path(r"C:\Program Files\Python311\python.exe"),
    Path(r"D:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"),
    Path(sys.executable)
]

chosen_python = None
for p in python_candidates:
    if p.exists():
        chosen_python = p
        break

if not chosen_python:
    chosen_python = Path(sys.executable)

print(f"Launching Coonoor GeoAI Server using: {chosen_python}")
print("Access WebGIS Application at: http://localhost:8080")
print("Access OpenAPI Documentation at: http://localhost:8080/docs")

try:
    subprocess.run([str(chosen_python), str(SCRIPT_PATH)], check=True)
except KeyboardInterrupt:
    print("\nServer stopped.")
