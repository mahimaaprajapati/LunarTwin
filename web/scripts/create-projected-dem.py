
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling

ROOT = Path(__file__).resolve().parents[2]

SOURCE = (
    ROOT
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "LOLA_south_pole_elevation_118m.tif"
)

OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "public"
    / "lunar-dem-projected-360.json"
)

GRID_SIZE = 360

if not SOURCE.exists():
    raise FileNotFoundError(
        f"Original DEM not found:\n{SOURCE}\n"
        "Update SOURCE to the actual TIFF location."
    )

with rasterio.open(SOURCE) as src:
    data = src.read(
        1,
        out_shape=(GRID_SIZE, GRID_SIZE),
        masked=True,
        resampling=Resampling.bilinear,
    )

    transform = src.transform * src.transform.scale(
        src.width / GRID_SIZE,
        src.height / GRID_SIZE,
    )

    # Keep NoData cells as NaN during processing.
    elevations_array = np.asarray(
        data.filled(np.nan),
        dtype=np.float64,
    )
        # Preserve the original raster's NoData boundary.
    elevations_array[0, :] = np.nan

    height, width = elevations_array.shape

    # Coordinates are pixel centers, in kilometres.
    x_km = [
        (transform.c + (c + 0.5) * transform.a) / 1000
        for c in range(width)
    ]

    y_km = [
        (transform.f + (r + 0.5) * transform.e) / 1000
        for r in range(height)
    ]

    # JSON null represents invalid / NoData elevations.
    elevations = [
        [
            round(float(v), 2) if np.isfinite(v) else None
            for v in row
        ]
        for row in elevations_array
    ]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

payload = {
    "width": width,
    "height": height,
    "x_km": x_km,
    "y_km": y_km,
    "elevations": elevations,
    "source": "LOLA south-pole elevation DEM",
    "horizontal_units": "km",
    "vertical_units": "meters",
    "crs": "Moon Simple Cylindrical",
}

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(payload, f, separators=(",", ":"))

valid_count = int(np.isfinite(elevations_array).sum())
invalid_count = elevations_array.size - valid_count

print(f"Created: {OUTPUT}")
print(f"Grid: {width} x {height}")
print(f"Valid cells: {valid_count}")
print(f"NoData cells: {invalid_count}")
print(f"X range: {min(x_km):.3f} to {max(x_km):.3f} km")
print(f"Y range: {min(y_km):.3f} to {max(y_km):.3f} km")
print("Done.")
