
import os
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

BASE = os.path.dirname(os.path.abspath(__file__))

source_path = os.path.join(
    BASE, "07_raw_data", "Illumination",
    "AVGVISIB_85S_060M_201608.tiff"
)

reference_path = os.path.join(
    BASE, "08_processed_data", "DEM",
    "Shackleton_LOLA_80M_crop.tif"
)

output_path = os.path.join(
    BASE, "08_processed_data", "Illumination",
    "Shackleton_average_illumination_80M.tif"
)

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with rasterio.open(source_path) as src, rasterio.open(reference_path) as ref:
    # Rasterio exposes the scale separately from the stored integer values.
    # Convert to physical values once before resampling.
    raw = src.read(1, masked=True).astype("float32")
    scale = src.scales[0]
    offset = src.offsets[0]

    values = raw.filled(np.nan) * scale + offset
    values[~np.isfinite(values)] = np.nan

    destination = np.full(
        (ref.height, ref.width), np.nan, dtype=np.float32
    )

    reproject(
        source=values,
        destination=destination,
        src_transform=src.transform,
        src_crs=src.crs,
        src_nodata=np.nan,
        dst_transform=ref.transform,
        dst_crs=ref.crs,
        dst_nodata=np.nan,
        resampling=Resampling.bilinear,
    )

    profile = ref.profile.copy()
    profile.update(
        driver="GTiff",
        count=1,
        dtype="float32",
        nodata=np.nan,
        compress="deflate",
    )

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(destination, 1)
        dst.set_band_description(
            1, "Average solar illumination (scaled source values)"
        )
        dst.update_tags(
            SOURCE_PRODUCT="AVGVISIB_85S_060M_201608",
            SOURCE_SCALE_FACTOR=str(scale),
            SOURCE_OFFSET=str(offset),
            RESAMPLING="bilinear",
            REFERENCE_GRID="Shackleton_LOLA_80M_crop.tif",
            NOTE="Verify physical units from official product documentation."
        )

print("Created:", output_path)
print("Output shape:", destination.shape)
print("Valid pixels:", int(np.isfinite(destination).sum()), "/", destination.size)
if np.isfinite(destination).any():
    print("Scaled value range:",
          float(np.nanmin(destination)),
          "to",
          float(np.nanmax(destination)))
