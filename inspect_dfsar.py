import rasterio
import glob
import os
import numpy as np

root = "MOON_DATASET/08_processed_data/Radar/DFSAR/20260308"

files = glob.glob(
    os.path.join(root, "**", "*.tif"),
    recursive=True
)

print("DFSAR RASTERS:", len(files))

for f in files:
    print("\n" + "=" * 70)
    print(os.path.relpath(f, root))

    with rasterio.open(f) as r:
        print("CRS:", r.crs)
        print("RESOLUTION:", r.res)
        print("SIZE:", r.width, "x", r.height)
        print("DTYPE:", r.dtypes[0])
        print("NODATA:", r.nodata)
        print(
            "BOUNDS:",
            tuple(round(x, 2) for x in r.bounds)
        )

        data = r.read(1, masked=True)

        print("VALID PIXELS:", data.count())

        if data.count() > 0:
            print("MIN:", float(data.min()))
            print("MAX:", float(data.max()))
            print(
                "MEAN:",
                float(data.mean())
            )