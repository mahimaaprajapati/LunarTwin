
import rasterio
from rasterio.windows import from_bounds

source_path = (
    "MOON_DATASET/07_raw_data/"
    "LOLA_80S_80M/ldem_80s_80m.lbl"
)

output_path = (
    "MOON_DATASET/08_processed_data/DEM/"
    "Shackleton_LOLA_80M_crop.tif"
)

# Provisional Shackleton centre in lunar projected coordinates (metres)
center_x = 7690.243761836725
center_y = -6402.723035824016
half_size = 20_000  # 20 km on each side

with rasterio.open(source_path) as src:
    bounds = (
        center_x - half_size,
        center_y - half_size,
        center_x + half_size,
        center_y + half_size,
    )

    window = from_bounds(*bounds, transform=src.transform)
    window = window.round_offsets().round_lengths()

    data = src.read(1, window=window)
    transform = src.window_transform(window)

    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        transform=transform,
        compress="deflate",
    )

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(data, 1)
        dst.update_tags(
            SOURCE="NASA LRO LOLA LDEM_80S_80M",
            REGION="Shackleton candidate region",
            NOTE="Provisional crop; geographic placement requires validation.",
        )

    print("Crop created:", output_path)
    print("Dimensions:", data.shape)
    print("Pixel size:", src.res)
    print("Crop bounds:", bounds)
    print("NoData pixels:", int((data == src.nodata).sum()))
    print("Raw DN range:", int(data[data != src.nodata].min()),
          int(data[data != src.nodata].max()))
