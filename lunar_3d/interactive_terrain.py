
from pathlib import Path
import webbrowser

import numpy as np
import rasterio
import plotly.graph_objects as go


# ============================================================
# 1. PATHS AND SETTINGS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DEM_PATH = (
    ROOT
    / "MOON_DATASET"
    / "08_processed_data"
    / "DEM"
    / "Shackleton_LOLA_80M_crop.tif"
)

OUTPUT_PATH = ROOT / "lunar_3d" / "lola_3d_viewer.html"

SCALE_FACTOR = 0.5
DOWNSAMPLE_STEP = 2


# ============================================================
# 2. LOAD THE SHACKLETON CANDIDATE DEM
# ============================================================

print("Loading LOLA DEM...")

with rasterio.open(DEM_PATH) as src:
    elevation = src.read(1).astype(np.float32)
    transform = src.transform
    nodata = src.nodata
    resolution = src.res
    crs = src.crs
    source_tags = src.tags()

print("DEM loaded.")
print("File:", DEM_PATH)
print("Original shape:", elevation.shape)
print("Resolution:", resolution)
print("CRS:", crs)

# Handle NoData before applying the scale factor.
if nodata is not None:
    elevation[elevation == nodata] = np.nan

# The crop stores raw LOLA digital numbers.
# The label's scale factor is 0.5 m per DN.
# Values are relative to the product's reference radius;
# they are not verified geoid-relative elevations.
elevation *= SCALE_FACTOR

valid = np.isfinite(elevation)

if not np.any(valid):
    raise ValueError("The DEM contains no valid elevation pixels.")

valid_values = elevation[valid]

print("\nElevation information")
print("---------------------")
print("Minimum:", float(valid_values.min()), "m")
print("Maximum:", float(valid_values.max()), "m")
print("Mean:", float(valid_values.mean()), "m")
print("Valid pixels:", int(valid.sum()))


# ============================================================
# 3. DOWNSAMPLE FOR INTERACTIVE VISUALIZATION
# ============================================================

# This reduces browser rendering load only.
# The source DEM is not modified.
step = DOWNSAMPLE_STEP

Z = elevation[::step, ::step]

rows, cols = np.indices(Z.shape)

# Pixel-centre coordinates from the raster's affine transform.
X = transform.c + (cols * step + 0.5) * transform.a
Y = transform.f + (rows * step + 0.5) * transform.e

# Keep NoData as gaps in the displayed surface.
Z = np.where(np.isfinite(Z), Z, np.nan)

print("\nDisplay grid:", Z.shape)


# ============================================================
# 4. CREATE INTERACTIVE 3D TERRAIN
# ============================================================

print("Creating interactive 3D terrain...")

fig = go.Figure(
    data=[
        go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale="Earth",
            connectgaps=False,
            colorbar=dict(
                title="Height relative<br>to reference radius (m)"
            ),
            hovertemplate=(
                "Projected X: %{x:.1f} m<br>"
                "Projected Y: %{y:.1f} m<br>"
                "Height: %{z:.1f} m"
                "<extra></extra>"
            ),
            lighting=dict(
                ambient=0.65,
                diffuse=0.8,
                specular=0.25,
                roughness=0.85,
                fresnel=0.1,
            ),
            lightposition=dict(x=1000, y=1000, z=2000),
        )
    ]
)


# ============================================================
# 5. LUNARTWIN VISUAL STYLE
# ============================================================

fig.update_layout(
    title=dict(
        text="LUNARTWIN | SHACKLETON CRATER — LOLA 80 m DEM",
        x=0.5,
        xanchor="center",
        font=dict(size=20, color="#E8EEFF"),
    ),
    paper_bgcolor="#0B1018",
    plot_bgcolor="#0B1018",
    font=dict(
        family="Arial, sans-serif",
        color="#D7E0EF",
    ),
    scene=dict(
        bgcolor="#0B1018",
        xaxis=dict(
            title="Lunar projected X (m)",
            backgroundcolor="#111A27",
            gridcolor="#29374A",
            zerolinecolor="#53647B",
            showbackground=True,
        ),
        yaxis=dict(
            title="Lunar projected Y (m)",
            backgroundcolor="#111A27",
            gridcolor="#29374A",
            zerolinecolor="#53647B",
            showbackground=True,
        ),
        zaxis=dict(
            title="Height relative to reference radius (m)",
            backgroundcolor="#111A27",
            gridcolor="#29374A",
            zerolinecolor="#53647B",
            showbackground=True,
        ),
        aspectmode="data",
        camera=dict(
            eye=dict(x=1.6, y=1.6, z=1.1),
        ),
    ),
    margin=dict(l=0, r=0, t=65, b=0),
    showlegend=False,
)


# ============================================================
# 6. SAVE AND OPEN HTML VIEWER
# ============================================================

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fig.write_html(
    str(OUTPUT_PATH),
    include_plotlyjs=True,
    full_html=True,
    config={
        "responsive": True,
        "displaylogo": False,
        "scrollZoom": True,
    },
)

print("\n" + "=" * 44)
print("INTERACTIVE TERRAIN VIEWER CREATED")
print("=" * 44)
print("Viewer:", OUTPUT_PATH)
print("Controls:")
print("  Left drag    - Rotate")
print("  Right drag   - Pan")
print("  Scroll       - Zoom")
print("  Hover        - Inspect projected coordinates and height")
print("  Double-click - Reset view")
print("=" * 44)

webbrowser.open(OUTPUT_PATH.as_uri())
