
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine, xy

root = Path(r"C:\Users\dell 5400\LunarTwin")

source = (
    root
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "LOLA_south_pole_elevation_118m.tif"
)

# Write to a separate test file. Do not overwrite lunar-dem.json.
output = root / "web" / "public" / "lunar-dem-360.json"

width = 360
height = 360
lunar_radius = 1737400.0

with rasterio.open(source) as ds:
    elevation = ds.read(
        1,
        out_shape=(height, width),
        resampling=Resampling.bilinear,
        masked=True,
    )

    transform = ds.transform * Affine.scale(
        ds.width / width,
        ds.height / height,
    )

    longitudes = []
    for col in range(width):
        x, _ = xy(transform, 0, col, offset="center")
        longitudes.append(round(math.degrees(x / lunar_radius), 6))

    latitudes = []
    for row in range(height):
        _, y = xy(transform, row, 0, offset="center")
        latitudes.append(round(math.degrees(y / lunar_radius), 6))

    values = elevation.filled(np.nan)

    elevations = [
        [
            None if not np.isfinite(value) else round(float(value), 2)
            for value in row
        ]
        for row in values
    ]

output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    json.dumps(
        {
            "width": width,
            "height": height,
            "longitudes": longitudes,
            "latitudes": latitudes,
            "elevations": elevations,
            "source": "LOLA south-pole elevation DEM",
            "units": "meters",
        }
    ),
    encoding="utf-8",
)

print("Created:", output)
print("Grid:", width, "x", height)
print("Valid elevation cells:", sum(
    value is not None
    for row in elevations
    for value in row
))
print("File size:", round(output.stat().st_size / 1024, 1), "KB")
