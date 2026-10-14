import rasterio
import os
import numpy as np


layers = {
    "DEM (Elevation)": (
        "MOON_DATASET/08_processed_data/DEM/"
        "LOLA_south_pole_elevation_118m.tif"
    ),

    "Slope": (
        "MOON_DATASET/08_processed_data/TERRAIN/"
        "Slope/LOLA_slope_degrees_118m.tif"
    ),

    "Aspect": (
        "MOON_DATASET/08_processed_data/TERRAIN/"
        "Aspect/LOLA_aspect_degrees_118m.tif"
    ),

    "Surface Roughness": (
        "MOON_DATASET/08_processed_data/TERRAIN/"
        "Roughness/LOLA_roughness_range_3x3_118m.tif"
    )
}


for name, path in layers.items():

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("Path:")
    print(path)

    if not os.path.exists(path):
        print("❌ FILE NOT FOUND")
        continue

    print("✅ FILE FOUND")

    with rasterio.open(path) as src:

        print("\nDimensions:")
        print("Width:", src.width)
        print("Height:", src.height)
        print("Bands:", src.count)

        print("\nResolution:")
        print(src.res)

        print("\nCRS:")
        print(src.crs)

        print("\nNoData:")
        print(src.nodata)

        print("\nBounds:")
        print(src.bounds)

        data = src.read(1).astype(float)

        if src.nodata is not None:
            data[data == src.nodata] = np.nan

        valid = data[np.isfinite(data)]

        if len(valid) > 0:

            print("\nValue range:")
            print("Minimum:", valid.min())
            print("Maximum:", valid.max())
            print("Mean:", valid.mean())
            print("Valid pixels:", len(valid))

        else:
            print("⚠ No valid pixels found")


print("\n")
print("=" * 70)
print("TERRAIN LAYER INSPECTION COMPLETE")
print("=" * 70)