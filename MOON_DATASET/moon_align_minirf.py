import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

radar_path = (
    "MOON_DATASET/07_raw_data/Radar/MiniRF/"
    "global_cpr_128ppd_simp_0c.lbl"
)

terrain_path = (
    "MOON_DATASET/08_processed_data/DEM/"
    "Shackleton_LOLA_80M_crop.tif"
)

output_path = (
    "MOON_DATASET/08_processed_data/Radar/"
    "Shackleton_CPR_80M.tif"
)

# Open the terrain crop: this defines the output grid.
with rasterio.open(terrain_path) as terrain:
    dst_transform = terrain.transform
    dst_crs = terrain.crs
    dst_shape = (terrain.height, terrain.width)
    dst_profile = terrain.profile.copy()

# Read only the source raster's values needed for reprojection.
with rasterio.open(radar_path) as radar:
    # Convert to float32 and explicitly mask PDS missing values.
    src = radar.read(1, masked=True).astype("float32")
    src_array = src.filled(np.nan)

    # The PDS label's missing constant becomes a huge negative
    # float32 value when read by GDAL, so mask it explicitly.
    src_array[src_array < -1e30] = np.nan

    dst = np.full(dst_shape, np.nan, dtype=np.float32)

    reproject(
        source=src_array,
        destination=dst,
        src_transform=radar.transform,
        src_crs=radar.crs,
        src_nodata=np.nan,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_nodata=np.nan,
        resampling=Resampling.nearest,
        init_dest_nodata=True,
    )

# Write a single-band float32 GeoTIFF with NaN NoData.
dst_profile.update(
    driver="GTiff",
    count=1,
    dtype="float32",
    nodata=np.nan,
    compress="deflate",
)

import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with rasterio.open(output_path, "w", **dst_profile) as out:
    out.write(dst, 1)
    out.set_band_description(1, "Mini-RF circular polarization ratio (CPR)")
    out.update_tags(
        source="LRO Mini-RF global CPR mosaic",
        product_id="GLOBAL_CPR_128PPD_SIMP_0C",
        resampling="nearest",
        target_grid="Shackleton_LOLA_80M_crop.tif",
        limitation="Partial radar coverage; missing values preserved",
    )

valid = np.isfinite(dst)
print("Created:", output_path)
print("Grid:", dst.shape)
print("Valid pixels:", int(valid.sum()), "/", dst.size)
print("Coverage:", round(100 * valid.mean(), 2), "%")
if valid.any():
    print("CPR range:", float(dst[valid].min()), "to", float(dst[valid].max()))