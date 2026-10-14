# Lunar Dataset — Data Dictionary

## lunar_features

| Column | Description | Source |
|---|---|---|
| feature_id | Unique ID created for this project | Project |
| feature_name | Official lunar feature name | IAU/USGS |
| feature_type | Type of lunar feature | IAU/USGS |
| latitude | Center latitude in decimal degrees | IAU/USGS |
| longitude | Center longitude in decimal degrees | IAU/USGS |
| diameter_km | Feature diameter in kilometres | IAU/USGS |
| north_latitude | Northern boundary | IAU/USGS |
| south_latitude | Southern boundary | IAU/USGS |
| east_longitude | Eastern boundary | IAU/USGS |
| west_longitude | Western boundary | IAU/USGS |
| hemisphere | Lunar hemisphere | Derived |
| region | Geographic region | Derived/Source |
| parent_feature | Parent geological/geographical feature | IAU/USGS |
| approval_status | IAU naming status | IAU/USGS |
| approval_date | Date of approval | IAU/USGS |
| origin | Origin of feature name | IAU/USGS |
| iau_reference | Official IAU reference | IAU/USGS |
| source_id | Link to source catalogue | Project |

**Shackleton LOLA elevation (80 m grid)**

- Source: `Shackleton_LOLA_80M_crop.tif`
- Conversion: raw pixel value × 0.5 m
- Units: metres relative to the LOLA reference radius of 1,737,400 m
- Derived layer: `Shackleton_height_80M.tif`
- Terrain stack: Band 1 contains the same converted elevation values.
- Limitation: geographic placement and vertical reference conventions still require final validation before scientific interpretation.

## Dataset Readiness and Limitations

**Current status: Structurally checked; scientific validation pending.**

### Validated structural checks
- Core terrain and illumination rasters are present.
- The terrain and illumination outputs share a 500 × 500 grid, 80 m pixel resolution, CRS, and spatial bounds.
- All four terrain-stack bands match their corresponding individual rasters: elevation, slope, aspect, and roughness.
- The terrain rasters currently contain 250,000 valid pixels each. This confirms file-level validity, not independent scientific validation.

### Elevation and terrain limitations
- The source LOLA crop contains raw values converted to metres using a factor of 0.5. These values are relative to the LOLA reference radius of 1,737,400 m; they must not be described as geoid-relative elevation without the required reference conversion.
- The terrain crop's geographic placement and vertical reference conventions still require independent validation.
- Slope and roughness derivation methods, units, and neighbourhood settings must be documented before scientific interpretation.
- Aspect ranges from 0 to approximately 360 degrees. For machine-learning use, encode this circular variable appropriately, such as with sine and cosine features.
- The existing all-one terrain mask does not establish independent source-data validity.

### Illumination limitations
- The average-illumination output is aligned to the terrain grid at the raster level.
- Physical interpretation, source-to-target geographic alignment, and resampling behaviour still require final validation.
- Preserve missing-data information; do not treat missing illumination as zero illumination.

### Excluded or incomplete inputs
- **Mini-RF CPR:** Exclude `Shackleton_CPR_80M.tif` from machine-learning inputs. The current reprojection produced implausible values and failed diagnostic testing.
- **Optical imagery:** The available candidate covers only part of the terrain crop. Do not interpret uncovered pixels as zero or complete coverage.
- **Additional radar products:** DFSAR coverage and compatibility remain unverified for the Shackleton analysis grid.

### Machine-learning readiness
The current layers are not yet approved as a fully validated scientific multimodal dataset. Any exploratory model must use explicitly approved inputs, preserve NoData, record source provenance, and disclose unresolved geospatial and feature-engineering limitations.

### Next validation tasks
1. Independently validate the lunar geographic placement and vertical reference of the terrain source.
2. Document the algorithms, units, and settings used to derive slope, aspect, and roughness.
3. Validate illumination geolocation and physical scaling.
4. Record the optical coverage footprint and exclude the failed CPR output.
5. Update the dataset catalogue and rerun final quality checks before handoff.