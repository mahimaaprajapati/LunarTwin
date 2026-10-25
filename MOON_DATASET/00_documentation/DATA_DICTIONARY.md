# Lunar Dataset ? Data Dictionary

## 1. Feature catalogue: `lunar_features`

| Column | Description | Source |
|---|---|---|
| `feature_id` | Unique ID created for this project | Project |
| `feature_name` | Official lunar feature name | IAU/USGS |
| `feature_type` | Type of lunar feature | IAU/USGS |
| `latitude` | Center latitude in decimal degrees | IAU/USGS |
| `longitude` | Center longitude in decimal degrees | IAU/USGS |
| `diameter_km` | Feature diameter in kilometres | IAU/USGS |
| `north_latitude` | Northern boundary | IAU/USGS |
| `south_latitude` | Southern boundary | IAU/USGS |
| `east_longitude` | Eastern boundary | IAU/USGS |
| `west_longitude` | Western boundary | IAU/USGS |
| `hemisphere` | Lunar hemisphere | Derived |
| `region` | Geographic region | Derived/Source |
| `parent_feature` | Parent geological/geographical feature | IAU/USGS |
| `approval_status` | IAU naming status | IAU/USGS |
| `approval_date` | Date of approval | IAU/USGS |
| `origin` | Origin of feature name | IAU/USGS |
| `iau_reference` | Official IAU reference | IAU/USGS |
| `source_id` | Link to source catalogue | Project |

## 2. Shackleton elevation and terrain

### LOLA elevation (80 m grid)

- Source: `Shackleton_LOLA_80M_crop.tif`
- Conversion currently applied: raw pixel value ? 0.5 m.
- Units: metres relative to the LOLA reference radius of 1,737,400 m, according to the current project documentation.
- Derived elevation layer: `Shackleton_height_80M.tif`.
- Terrain stack: `Shackleton_terrain_stack_80M.tif`, with four bands in this order: elevation, slope, aspect, and roughness.
- Related layers: `Shackleton_slope_80M.tif`, `Shackleton_aspect_80M.tif`, `Shackleton_roughness_80M.tif`, and `Shackleton_terrain_valid_mask_80M.tif`.

The elevation conversion, geographic placement, and vertical reference conventions still require independent validation before scientific interpretation.

### Terrain derivation and encoding

- The current terrain rasters have a 500 ? 500 grid and 250,000 valid pixels each.
- Slope and roughness algorithms, units, neighbourhood settings, and edge handling must be documented before scientific interpretation.
- Aspect ranges from approximately 0 to 360 degrees. For machine-learning use, consider circular encoding, such as sine and cosine features.
- The existing all-one terrain mask describes the current crop's valid-pixel mask; it does not independently establish the scientific validity of the source data.
- Preserve each raster's NoData value and document any transformations applied before analysis.

## 3. Illumination

- Processed layer: `Illumination/Shackleton_average_illumination_80M.tif`.
- The output matches the terrain grid at the raster level: 500 ? 500 pixels, 80 m resolution, CRS, and bounds.
- The source-to-target geographic alignment, physical meaning, value scaling, and resampling behaviour still require validation.
- Preserve missing-data information. Do not interpret missing illumination values as zero illumination.

## 4. Radar data

### Mini-RF CPR

- Original source: `07_raw_data/Radar/MiniRF/global_cpr_128ppd_simp_0c.img` and its `.lbl` label file.
- A Shackleton-aligned sample layer was generated as `Shackleton_CPR_aligned_80M.tif`.
- The aligned layer's finite values were checked against the original source samples and matched in the comparison performed.
- The aligned layer contains negative values and unusually large positive values also present in the source samples. Their scientific interpretation has not been established; do not silently clip or replace them.
- `Radar/Shackleton_CPR_80M.tif` is an alternate output with implausible extreme values and unresolved georeferencing/reprojection concerns. **Do not use this alternate layer as a trusted machine-learning input** until its transformation is independently verified.
- CPR coverage is partial. Preserve NoData and document the source-to-target sampling method.

### DFSAR

The DFSAR polarization rasters and derived products are stored under `Radar/DFSAR/20260308/`.

- Polarization inputs: HH, HV, VH, and VV.
- Derived products include HH ? VV difference, HV/HH ratio, and VH/VV ratio.
- The polarization rasters share a 25 m grid. The two ratio products were checked against their corresponding formulas within floating-point tolerance; the HH ? VV difference was also checked against the input values.
- The polarization source rasters contain extensive zero-valued areas. Whether these zeros represent background/no coverage or valid measurements has not been confirmed.
- Ratio layers have substantially fewer valid pixels than the source rasters. Treat this as a coverage/denominator-related property requiring documented interpretation, not as proof of scientific validity.
- DFSAR's geographic overlap with Shackleton and its compatibility with the 80 m analysis grid remain unverified. Do not treat it as an approved Shackleton feature layer yet.

## 5. Other source and processed data

The dataset also contains LOLA and LROC catalogues, feature-linked tables, observation tables, research/source catalogues, a wider-area 118 m elevation product, and site-specific elevation/imagery inputs. These represent different source products and spatial extents; they should not all be expected to match the Shackleton 80 m reference grid.

Check each product's own metadata, CRS, bounds, pixel size, NoData convention, and provenance before combining it with other layers.

## 6. Dataset readiness and limitations

**Current status: `PARTIALLY_VALIDATED_SCIENTIFIC_REVIEW_PENDING`.**

### Checks completed

- The validation report inventories 23 rasters.
- The core Shackleton terrain and average-illumination outputs share a 500 ? 500 reference grid.
- Terrain-stack bands were checked against their corresponding component rasters.
- DFSAR grid consistency and derived-product formulas were checked.
- The aligned CPR output was compared against original source samples.
- Detailed check results and unresolved items are recorded in `08_processed_data/dataset_validation_report.json`.

These checks establish file/grid consistency and selected formula/source-sample relationships. They do not, by themselves, establish scientific correctness or full geospatial compatibility.

### Pending validation tasks

1. Independently validate the lunar geographic placement and vertical reference of the terrain source.
2. Document the algorithms, units, parameters, and neighbourhood settings used to derive slope, aspect, and roughness.
3. Validate illumination geolocation, physical scaling, and resampling.
4. Confirm the meaning of zero-valued DFSAR pixels and document the effective coverage footprint.
5. Review CPR outliers against authoritative product documentation and retain source-faithful values unless a justified correction is established.
6. Record optical and radar coverage footprints and verify their overlap with the Shackleton study area.
7. Update the dataset catalogue and rerun quality checks before scientific handoff.

### Machine-learning readiness

The current layers are **not approved as a fully validated scientific multimodal dataset**. Exploratory work should use explicitly approved inputs, preserve NoData and provenance, distinguish missing coverage from measured zero values, and disclose unresolved geospatial and feature-engineering limitations.

## 7. Validation record

Refer to `08_processed_data/dataset_validation_report.json` for the raster inventory and recorded checks. A backup of the dictionary was created before this edit. Backup files are archival copies and should not be treated as active dataset documentation.
