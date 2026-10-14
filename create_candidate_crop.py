
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parent

SOURCE = (
    ROOT
    / "MOON_DATASET"
    / "07_raw_data"
    / "LOLA_80S_80M"
    / "ldem_80s_80m.lbl"
)

OUTPUT = (
    ROOT
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "Shackleton_LOLA_80M_candidate.tif"
)

# Candidate source window: 500 x 500 pixels.
ROW_START = 3630
COL_START = 3453
SIZE = 500

with rasterio.open(SOURCE) as src:
    window = Window(COL_START, ROW_START, SIZE, SIZE)
    data = src.read(1, window=window)

    if data.shape != (SIZE, SIZE):
        raise ValueError(f"Unexpected crop shape: {data.shape}")

    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        width=SIZE,
        height=SIZE,
        transform=rasterio.windows.transform(window, src.transform),
        compress="deflate",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(OUTPUT, "w", **profile) as dst:
        dst.write(data, 1)
        dst.update_tags(
            REGION="Shackleton candidate region - placement unverified",
            SOURCE="NASA LRO LOLA LDEM_80S_80M",
            SOURCE_ROW_START=str(ROW_START),
            SOURCE_COL_START=str(COL_START),
            NOTE="Candidate crop; geographic placement must be independently validated.",
        )

    print("Candidate crop created:", OUTPUT)
    print("Shape:", data.shape)
    print("Source window row:", ROW_START)
    print("Source window column:", COL_START)
    print("Data type:", data.dtype)
    print("NoData:", src.nodata)
    print("Transform:", rasterio.windows.transform(window, src.transform))
    print("Minimum:", int(data[data != src.nodata].min()))
    print("Maximum:", int(data[data != src.nodata].max()))
