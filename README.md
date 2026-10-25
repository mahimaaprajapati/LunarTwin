# LunarTwin

LunarTwin is a lunar exploration project that brings together lunar terrain data, scientific observations, resource-assessment inputs, and geospatial visualisation to support exploration of potential lunar landing and study sites.

## Project goals

- Explore lunar terrain and elevation.
- Organise and document datasets from lunar missions.
- Prepare geospatial layers for future analysis.
- Support future AI/ML-based resource assessment and mission-planning workflows.
- Visualise lunar terrain and relevant scientific data.

## Repository structure

- `MOON_DATASET/` — Dataset catalogues, observations, source records, documentation, and processed lunar data.
- `lunar_3d/` — Terrain inspection and 3D visualisation tools.
- Root-level Python scripts — Dataset checks, processing utilities, and validation tools.

## Dataset documentation

Start here:

- [Dataset README](MOON_DATASET/README.md)
- [Data dictionary](MOON_DATASET/00_documentation/DATA_DICTIONARY.md)
- [Dataset catalogue](MOON_DATASET/03_dataset_catalogue/dataset_catalogue.csv)
- [Shackleton dataset manifest](MOON_DATASET/08_processed_data/shackleton_dataset_manifest.csv)
- [Dataset validation report](MOON_DATASET/08_processed_data/dataset_validation_report.json)

The dataset README describes the directory structure, principal data products, provenance, and known limitations.

## Current status

**Status: Partially validated; scientific review pending.**

Dataset organisation and several structural, grid-alignment, and value checks have been completed. However, scientific validation is not complete. Some products remain provisional, CPR outliers require further review, and DFSAR compatibility with the Shackleton analysis area remains unverified.

Do not interpret the current dataset as a fully validated scientific product or treat every raster as an approved analysis layer.

## Raw data and version control

Large raw scientific inputs under `MOON_DATASET/07_raw_data/` are excluded from ordinary Git tracking. They must be obtained from their original sources and placed in the expected directory structure before running workflows that depend on them.

See `MOON_DATASET/README.md` for further details.

## Development

Use a Python environment with the dependencies required by the individual scripts. Check each script's inputs, outputs, and assumptions before running it.
