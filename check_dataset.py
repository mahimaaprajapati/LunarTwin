
import os
import numpy as np
import rasterio

base = "MOON_DATASET/08_processed_data"

files = [
    "DEM/Shackleton_LOLA_80M_crop.tif",
    "DEM/Shackleton_height_80M.tif",
    "DEM/Shackleton_slope_80M.tif",
    "DEM/Shackleton_aspect_80M.tif",
    "DEM/Shackleton_roughness_80M.tif",
    "DEM/Shackleton_terrain_stack_80M.tif",
    "DEM/Shackleton_terrain_valid_mask_80M.tif",
    "Illumination/Shackleton_average_illumination_80M.tif",
]

for name in files:
    path = os.path.join(base, name)
    print(f"\n--- {name} ---")

    if not os.path.exists(path):
        print("MISSING")
        continue

    with rasterio.open(path) as ds:
        data = ds.read(1, masked=True)
        valid = data.compressed()

        print("Shape:", ds.shape)
        print("Bands:", ds.count)
        print("CRS:", ds.crs)
        print("Resolution:", ds.res)
        print("NoData:", ds.nodata)
        print("Valid pixels:", len(valid), "/", ds.width * ds.height)
        print("Bounds:", ds.bounds)

        if len(valid):
            print("Minimum:", float(valid.min()))
            print("Maximum:", float(valid.max()))

print("\nDataset check complete.")

print("\n--- Terrain stack consistency ---")

root = "MOON_DATASET/08_processed_data/DEM"
stack_path = os.path.join(root, "Shackleton_terrain_stack_80M.tif")

layers = [
    "Shackleton_height_80M.tif",
    "Shackleton_slope_80M.tif",
    "Shackleton_aspect_80M.tif",
    "Shackleton_roughness_80M.tif",
]

with rasterio.open(stack_path) as stack:
    for band, filename in enumerate(layers, start=1):
        with rasterio.open(os.path.join(root, filename)) as src:
            a = stack.read(band, masked=True).filled(np.nan)
            b = src.read(1, masked=True).filled(np.nan)

            same = (
                a.shape == b.shape
                and np.allclose(a, b, rtol=1e-5, atol=1e-5, equal_nan=True)
            )

            print(f"Band {band} vs {filename}: {'MATCH' if same else 'MISMATCH'}")
