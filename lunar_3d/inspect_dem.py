from pathlib import Path
import rasterio


# Find the LunarTwin repository root
ROOT = Path(__file__).resolve().parents[1]

# Path to the existing LOLA DEM
DEM_PATH = (
    ROOT
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "LOLA_south_pole_elevation_118m.tif"
)


print("LOLA DEM:")
print(DEM_PATH)

print("\nChecking if file exists...")

if not DEM_PATH.exists():
    print("❌ DEM NOT FOUND")
    print("Expected location:")
    print(DEM_PATH)
else:
    print("✅ DEM FOUND")

    with rasterio.open(DEM_PATH) as dem:

        print("\n========== DEM INFORMATION ==========")

        print("Width:", dem.width)
        print("Height:", dem.height)
        print("Number of bands:", dem.count)

        print("CRS:", dem.crs)

        print("Resolution:", dem.res)

        print("NoData value:", dem.nodata)

        print("\nBounds:")
        print(dem.bounds)

        print("\n====================================")