from pathlib import Path
import numpy as np

image_path = Path(
    "MOON_DATASET/07_raw_data/LOLA_80S_80M/ldem_80s_80m.img"
)

expected_size = 7600 * 7600 * 2

print("File exists:", image_path.exists())

if not image_path.exists():
    raise FileNotFoundError(image_path)

actual_size = image_path.stat().st_size
print("Actual size:", actual_size, "bytes")
print("Expected size:", expected_size, "bytes")
print("Size matches:", actual_size == expected_size)

if actual_size != expected_size:
    raise ValueError("Image size does not match the label.")

# Read-only interpretation of the PDS image:
# signed 16-bit little-endian integers.
pixels = np.fromfile(image_path, dtype="<i2").reshape(7600, 7600)

print("Shape:", pixels.shape)
print("Data type:", pixels.dtype)
print("Raw minimum:", int(pixels.min()))
print("Raw maximum:", int(pixels.max()))
print("Raw mean:", float(pixels.mean()))
print("Top-left 5x5 pixel values:")
print(pixels[:5, :5])


import math

# Shackleton Crater centre from the study-region specification
latitude_deg = -89.67
longitude_deg = 129.78

# Parameters from the LOLA label
moon_radius_m = 1_737_400
pixel_size_m = 80
line_offset = 3799.5
sample_offset = 3799.5

lat = math.radians(latitude_deg)
lon = math.radians(longitude_deg)

# South-polar stereographic coordinates
rho = 2 * moon_radius_m * math.tan(math.pi / 4 + lat / 2)
x = rho * math.sin(lon)
y = rho * math.cos(lon)

# PDS sample and line coordinates (zero-based)
sample = x / pixel_size_m + sample_offset
line = line_offset - y / pixel_size_m

print("\n--- Shackleton location estimate ---")
print("Projected X (m):", x)
print("Projected Y (m):", y)
print("Sample (column):", sample)
print("Line (row):", line)
print("Inside raster:", 0 <= sample < 7600 and 0 <= line < 7600)
