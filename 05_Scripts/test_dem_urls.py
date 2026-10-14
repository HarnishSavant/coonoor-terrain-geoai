import requests

candidates = [
    # Copernicus 30m GLO-30 on AWS Open Data (public, no auth)
    "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N11_00_E076_00_DEM/Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif",
    # Alternative Copernicus path
    "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_N11_00_E076_00_DEM/Copernicus_DSM_COG_10_N11_00_E076_00_DEM.tif",
    # OpenTopography SRTMGL1
    "https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south=11.2&north=11.45&west=76.6&east=76.9&outputFormat=GTiff",
    # AWS Mapzen / Terrain Tiles
    "https://s3.amazonaws.com/elevation-tiles-prod/geotiff/10/730/487.tif"
]

for url in candidates:
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        print(f"URL: {url[:70]}...\n  Status: {r.status_code}, Length: {r.headers.get('content-length')}")
    except Exception as e:
        print(f"URL: {url[:70]}...\n  Error: {e}")
