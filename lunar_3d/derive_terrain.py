
import os

import numpy as np
import rasterio
from scipy.ndimage import generic_filter

SOURCE_PATH = (
    "MOON_DATASET/08_processed_data/DEM/"
    "Shackleton_LOLA_80M_crop.tif"
)

OUTPUT_DIR = "MOON_DATASET/08_processed_data/DEM/"

SCALE_FACTOR = 0.5
PIXEL_SIZE = 80.0
ROUGHNESS_WINDOW = 5
OUTPUT_NODATA = -9999.0


def local_std(values):
    """Standard deviation of valid pixels in a local window."""
    valid = values[np.isfinite(values)]
    if valid.size == 0:
        return np.nan
    return float(np.std(valid))


with rasterio.open(SOURCE_PATH) as src:
    dn = src.read(1).astype(np.float32)
    source_nodata = src.nodata
    profile = src.profile.copy()

    valid = np.isfinite(dn)
    if source_nodata is not None:
        valid &= dn != source_nodata

    # Keep invalid pixels as NaN throughout the calculations.
    height = np.full(dn.shape, np.nan, dtype=np.float32)
    height[valid] = dn[valid] * SCALE_FACTOR

    # Calculate gradients only after temporarily filling invalid cells.
    # Derivatives at and near filled cells will be masked afterwards.
    if not np.any(valid):
        raise ValueError("The source raster contains no valid pixels.")

    fill_value = float(np.median(height[valid]))
    filled = np.where(valid, height, fill_value)

    # Array rows increase southward; columns increase eastward in raster
    # coordinates. Aspect is provisional until the lunar grid orientation
    # is independently verified.
    grad_row, grad_col = np.gradient(
        filled,
        PIXEL_SIZE,
        PIXEL_SIZE,
    )

    slope = np.degrees(
        np.arctan(np.hypot(grad_col, grad_row))
    ).astype(np.float32)

    # Mathematical direction of steepest descent in raster coordinates.
    # This is NOT yet a validated geographic compass aspect.
    aspect = (
        np.degrees(np.arctan2(-grad_col, -grad_row)) + 360.0
    ) % 360.0
    aspect = aspect.astype(np.float32)

    # Local standard deviation; windows ignore invalid source cells.
    roughness = generic_filter(
        height,
        function=local_std,
        size=ROUGHNESS_WINDOW,
        mode="constant",
        cval=np.nan,
    ).astype(np.float32)

    # Do not publish derivative values at invalid source pixels.
    for arr in (slope, aspect, roughness):
        arr[~valid] = np.nan

    profile.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=OUTPUT_NODATA,
        compress="deflate",
    )

    outputs = {
        "Shackleton_height_80M.tif": height,
        "Shackleton_slope_80M.tif": slope,
        "Shackleton_aspect_80M.tif": aspect,
        "Shackleton_roughness_80M.tif": roughness,
    }

    for filename, array in outputs.items():
        output_path = os.path.join(OUTPUT_DIR, filename)
        output_data = np.where(
            np.isfinite(array),
            array,
            OUTPUT_NODATA,
        ).astype(np.float32)

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(output_data, 1)
            dst.update_tags(
                SOURCE="NASA LRO LOLA LDEM_80S_80M",
                SCALE_FACTOR=str(SCALE_FACTOR),
                PIXEL_SIZE_M=str(PIXEL_SIZE),
                ROUGHNESS_METHOD="5x5 local standard deviation",
                ASPECT_NOTE=(
                    "Raster-coordinate direction; geographic orientation "
                    "not independently validated."
                ),
                REGION_NOTE=(
                    "Shackleton candidate region; geographic placement "
                    "still requires independent validation."
                ),
            )

        print("Created:", output_path)

    for filename, array in outputs.items():
        finite = array[np.isfinite(array)]
        if finite.size:
            print(
                filename,
                "| min:", float(finite.min()),
                "| max:", float(finite.max()),
                "| valid pixels:", int(finite.size),
            )
