# Study Region Specification

## 1. Study Region

**Primary study region:** Shackleton Crater

**Feature ID:** LUN-0008305

**Feature type:** Crater

**Hemisphere:** Southern

**Region:** Amundsen

**Centre latitude:** -89.67°

**Centre longitude:** 129.78°E

**Diameter:** 20.924982 km

**Official source:** USGS/IAU Moon Gazetteer

**IAU approval status:** Adopted by IAU

## 2. Region Boundary

The official feature catalogue provides the following geographic bounds:

- North latitude: -89.287°
- South latitude: -89.943°
- East longitude: 206.565°
- West longitude: 35.538°

**Important:** The longitude values in the IAU catalogue span a very large range compared with the reported crater diameter and centre coordinates. They are therefore preserved exactly as supplied by the catalogue and are **not interpreted or corrected at this stage**.

For initial processing, the crater centre and official catalogue record will be treated as the authoritative feature reference. A final processing polygon/bounding box should be established only after the exact study-region boundary representation is confirmed.

## 3. Coordinate Reference System

The existing repository LOLA DEM uses a custom lunar coordinate reference system:

- Projection: Equirectangular / Simple Cylindrical Moon
- Lunar radius: 1,737,400 m
- Central meridian: 0°
- Standard parallel: 0°
- Linear units: metres

The CRS is recorded in the existing DEM as a custom WKT definition.

**Status:** The exact CRS to be used for the final multimodal analysis grid is **not yet finalized**. It must be verified against the actual source products supplied for Shackleton before reprojection and resampling.

## 4. Required Data Coverage

The LunarTwin scientific processing pipeline is intended to produce a spatially aligned, analysis-ready multimodal dataset for Shackleton Crater.

Required source categories:

1. LOLA / DEM
2. DFSAR
3. OHRC / LROC optical data
4. Illumination/support datasets

The final common analysis grid and resolution will be selected after inspecting the actual source products and their spatial resolutions.

## 5. LOLA Source Identified in Catalogue

The LOLA product catalogue identifies the following relevant South-Pole DEM tile:

**Product:** `LDEM_1024_90S_75S_120_150`

**Latitude coverage:** 90°S–75°S

**Longitude coverage:** 120°E–150°E

**Source path in catalogue:**

`DATA/LOLA_GDR/CYLINDRICAL/IMG/LDEM_1024_90S_75S_120_150.LBL`

This tile covers the reported Shackleton centre at approximately **89.67°S, 129.78°E**.

A corresponding JP2 product is also catalogued:

`DATA/LOLA_GDR/CYLINDRICAL/JP2/LDEM_1024_90S_75S_120_150_JP2.LBL`

## 6. Local Data Availability

The exact `LDEM_1024_90S_75S_120_150` product is **not currently present** in the repository.

The repository does contain:

`MOON_DATASET/08_processed_data/DEM/LOLA_south_pole_elevation_118m.tif`

However, inspection of its CRS and bounds indicates that this raster covers approximately **80–90°S and 0–10°E** under its stored Simple Cylindrical Moon coordinate definition.

Therefore, this existing raster is **not currently treated as the Shackleton DEM**.

No Shackleton-specific slope, aspect, or roughness layers will be generated from it until the correct source DEM is verified.

## 7. Current Data Status

| Dataset | Required | Catalogue/source identified | Local Shackleton-ready data |
|---|---|---|---|
| LOLA / DEM | Yes | Yes | Exact tile not present |
| DFSAR | Yes | To be verified | Pending |
| OHRC / LROC | Yes | To be verified | Pending |
| Illumination | Yes | To be verified | Pending |

## 8. Processing Status

The study region has been identified and the relevant LOLA catalogue tile has been located.

The next scientific processing step is to obtain or locate the exact Shackleton source products supplied for the project, then verify:

- source/product ID
- acquisition information
- processing level
- spatial resolution
- CRS
- spatial coverage
- format
- NoData definition

Only after those checks will clipping, reprojection, resampling, co-registration, feature derivation, and multimodal fusion be performed.

## 9. Notes

This document intentionally records unresolved items rather than making unsupported assumptions.

In particular:

- The IAU longitude bounds are preserved as catalogued.
- The final study-region polygon/bounding box is not yet fixed.
- The final common CRS and analysis resolution are not yet fixed.
- The existing repository DEM is not assumed to represent Shackleton.
- The exact DFSAR, OHRC and illumination products still need to be verified.