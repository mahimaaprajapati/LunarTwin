from pathlib import Path

import numpy as np
import rasterio

import matplotlib
matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
# --------------------------------------------------
# 1. Locate the LunarTwin repository
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]


DEM_PATH = (
    ROOT
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "Shackleton_LOLA_80M_crop.tif"
)



# --------------------------------------------------
# 2. Read the LOLA DEM
# --------------------------------------------------

print("Loading LOLA DEM...")


with rasterio.open(DEM_PATH) as dem:
    elevation = dem.read(1).astype(float)
    transform = dem.transform
    nodata = dem.nodata

    if nodata is not None:
        elevation[elevation == nodata] = np.nan

    elevation *= 0.5

    print("DEM loaded successfully.")
    print("Shape:", elevation.shape)
    print("NoData:", nodata)



# --------------------------------------------------
# 3. Replace NoData with NaN
# --------------------------------------------------



# --------------------------------------------------
# 4. Create coordinate arrays
# --------------------------------------------------

height, width = elevation.shape

cols = np.arange(width)
rows = np.arange(height)

x = transform.c + cols * transform.a
y = transform.f + rows * transform.e


# --------------------------------------------------
# 5. Create 2D coordinate grid
# --------------------------------------------------

X, Y = np.meshgrid(x, y)


# --------------------------------------------------
# 6. Basic elevation information
# --------------------------------------------------

valid_elevation = elevation[~np.isnan(elevation)]

print("\nElevation information")
print("---------------------")
print("Minimum:", np.min(valid_elevation), "m")
print("Maximum:", np.max(valid_elevation), "m")
print("Mean:", np.mean(valid_elevation), "m")
print("Valid pixels:", len(valid_elevation))


# --------------------------------------------------
# 7. Create 3D terrain
# --------------------------------------------------

print("\nCreating 3D terrain...")


fig = plt.figure(figsize=(12, 9))

ax = fig.add_subplot(111, projection="3d")


surface = ax.plot_surface(
    X,
    Y,
    elevation,
    cmap="terrain",
    linewidth=0,
    antialiased=True
)


# --------------------------------------------------
# 8. Labels
# --------------------------------------------------

ax.set_title("LunarTwin - Shackleton Crater (LOLA 80 m DEM)")

ax.set_xlabel("X coordinate (m)")
ax.set_ylabel("Y coordinate (m)")
ax.set_zlabel("Elevation (m)")
ax.view_init(elev=35, azim=-60)
ax.set_box_aspect((1, 1, 0.65))

# --------------------------------------------------
# 9. Color bar
# --------------------------------------------------

fig.colorbar(
    surface,
    ax=ax,
    shrink=0.6,
    label="Elevation (m)"
)


# --------------------------------------------------
# 10. Display
# --------------------------------------------------

plt.tight_layout()

plt.show()