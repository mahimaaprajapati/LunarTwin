# LunarTwin ? Lunar Dataset

## 1. Overview

`MOON_DATASET` contains lunar feature catalogues, observations, source metadata, raw scientific inputs, and processed raster products prepared for the LunarTwin project.

The dataset brings together terrain, illumination, radar, and related geospatial information to support lunar exploration and future resource-assessment workflows.

**Validation status:** `PARTIALLY_VALIDATED_SCIENTIFIC_REVIEW_PENDING`

File integrity, selected raster-grid relationships, and certain derived-product calculations have been checked. These checks do not establish complete scientific validity or confirm that every data product is geographically compatible with the Shackleton study area.

## 2. Directory structure

| Directory | Contents |
|---|---|
| `00_documentation/` | Data dictionary and dataset documentation |
| `01_feature_catalogue/` | Lunar feature catalogue |
| `03_dataset_catalogue/` | Dataset and source-product catalogues |
| `04_observations/` | Lunar observation tables |
| `05_research/` | Research findings and paper records |
| `06_sources/` | Source references and provenance records |
| `07_raw_data/` | Original and downloaded scientific inputs |
| `08_processed_data/` | Processed rasters, derived features, manifests, catalogues, and validation report |

Some products have different spatial resolutions, extents, and purposes. They should not be assumed to share one grid simply because they belong to the same dataset.

## 3. Main data products

### Terrain and elevation

The processed DEM directory contains the Shackleton elevation crop, converted elevation layer, slope, aspect, roughness, terrain stack, and valid-pixel mask.

The current Shackleton terrain outputs use a 500 ? 500 grid with nominal 80 m pixel spacing. The terrain stack contains four bands in this order:

1. Elevation
2. Slope
3. Aspect
4. Roughness

The elevation conversion currently documented in the project applies a factor of 0.5 to the source LOLA pixel values. Geographic placement and vertical reference conventions still require independent validation.

### Illumination

`08_processed_data/Illumination/Shackleton_average_illumination_80M.tif` is the processed average-illumination layer aligned to the terrain grid at the raster level.

Its physical scaling, source-to-target geographic alignment, and resampling behaviour remain under review. Missing values must not be interpreted as zero illumination.

### Mini-RF CPR

The original Mini-RF CPR image and label are stored under `07_raw_data/Radar/MiniRF/`.

The project contains both a source-sample-checked aligned CPR layer and an alternate CPR raster with unresolved reprojection/georeferencing concerns. The alternate `Radar/Shackleton_CPR_80M.tif` must not be treated as a trusted machine-learning input until its transformation is independently verified.

The aligned output contains negative and unusually large values also found in source samples. Their scientific interpretation remains unresolved; values should not be silently clipped or replaced.

### DFSAR

DFSAR polarization inputs and derived products are stored under `08_processed_data/Radar/DFSAR/20260308/`.

The available products include HH, HV, VH, and VV polarization rasters, an HH ? VV difference layer, and HV/HH and VH/VV ratio layers. Selected grid and formula checks have passed. However, the meaning of extensive zero-valued source areas and the products' geographic overlap with Shackleton have not been fully established.

## 4. Documentation and validation

- **Data dictionary:** `00_documentation/DATA_DICTIONARY.md`
- **Validation report:** `08_processed_data/dataset_validation_report.json`
- **Study region specification:** `Study_Region_Specification.md`
- **Audit log:** `dataset_audit_log.txt`

The validation report records the raster inventory and additional checks. Consult it alongside the data dictionary before selecting layers for analysis.

## 5. Important limitations

- Geographic placement and vertical reference conventions of the terrain source require independent validation.
- Slope and roughness derivation methods, units, and neighbourhood settings need documentation.
- Illumination geolocation and physical scaling remain under review.
- The alternate CPR reprojection is unverified and should be excluded from trusted model inputs.
- DFSAR zero-value semantics and overlap with the Shackleton analysis area remain unresolved.
- Optical and radar coverage may be partial. Missing coverage must not be treated as a measured zero.
- Different source products may use different resolutions, extents, coordinate systems, and NoData conventions.

## 6. Use in machine learning

This dataset is not yet approved as a fully validated scientific multimodal dataset.

Before using layers together:

1. Check each layer's CRS, bounds, resolution, units, NoData convention, and provenance.
2. Confirm its geographic overlap with the study region.
3. Preserve missing-data information and distinguish missing coverage from real zero values.
4. Use only explicitly approved inputs and document transformations.
5. Report unresolved scientific and geospatial limitations with any results.

## 7. Large raw files and version control

Some raw scientific inputs are very large. In particular, the global Mini-RF CPR image is approximately 4.25 GB.

Raw data are currently excluded by the repository's `.gitignore` rule for `MOON_DATASET/07_raw_data/`. Do not remove that exclusion or commit the multi-gigabyte image to ordinary Git history without first deciding on a suitable distribution method, such as documenting its source and retrieval steps or using Git LFS where appropriate.

## 8. Current readiness

The dataset has undergone structural checks and selected formula/source-sample comparisons. Scientific review remains pending. The dataset should be described as partially validated, not as fully scientifically validated or ready for definitive multimodal modelling.
