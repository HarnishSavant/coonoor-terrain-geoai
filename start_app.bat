@echo off
title Coonoor GeoAI WebGIS Application
echo ============================================================
echo   COONOOR GEOAI TERRAIN ASSESSMENT WEBGIS APPLICATION
echo   Study Area: Coonoor Taluk, The Nilgiris, Tamil Nadu, India
echo ============================================================
echo.

cd /d "D:\Defence\MyProject1"

echo Starting FastAPI Backend and WebGIS Server...
echo Serving at: http://localhost:8080
echo OpenAPI Docs: http://localhost:8080/docs
echo.

start "" "http://localhost:8080"

if exist "C:\Program Files\Python311\python.exe" (
    "C:\Program Files\Python311\python.exe" "D:\Defence\MyProject1\05_Scripts\backend_api.py"
) else if exist "D:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" (
    "D:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "D:\Defence\MyProject1\05_Scripts\backend_api.py"
) else (
    python "D:\Defence\MyProject1\05_Scripts\backend_api.py"
)

pause
