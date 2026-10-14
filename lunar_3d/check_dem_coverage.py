import rasterio
from rasterio.transform import xy
import numpy as np


dem_path = (
    "MOON_DATASET/08_processed_data/DEM/"
    "LOLA_south_pole_elevation_118m.tif"
)

with rasterio.open(dem_path) as src:

    print("=" * 60)
    print("LOLA DEM GEOGRAPHIC COVERAGE")
    print("=" * 60)

    print("\nCRS:")
    print(src.crs)

    print("\nRaster bounds:")
    print(src.bounds)

    print("\nRaster size:")
    print(src.width, "x", src.height)

    print("\nPixel resolution:")
    print(src.res)

    # Four corner pixel centres
    corners = {
        "Top-left": (0, 0),
        "Top-right": (0, src.width - 1),
        "Bottom-left": (src.height - 1, 0),
        "Bottom-right": (src.height - 1, src.width - 1),
    }

    print("\nCorner coordinates in raster CRS:")

    for name, (row, col) in corners.items():

        x, y = xy(
            src.transform,
            row,
            col,
            offset="center"
        )

        print(f"{name}:")
        print(f"  X = {x:.3f} m")
        print(f"  Y = {y:.3f} m")

    print("\n" + "=" * 60)
    print("APPROXIMATE MOON LAT/LON")
    print("=" * 60)

    lunar_radius = 1737400.0

    for name, (row, col) in corners.items():

        x, y = xy(
            src.transform,
            row,
            col,
            offset="center"
        )

        longitude = np.degrees(x / lunar_radius)
        latitude = np.degrees(y / lunar_radius)

        print(f"{name}:")
        print(f"  Latitude  = {latitude:.6f}°")
        print(f"  Longitude = {longitude:.6f}°")

    print("\n" + "=" * 60)