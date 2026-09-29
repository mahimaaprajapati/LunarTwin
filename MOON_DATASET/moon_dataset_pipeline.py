"""
DIGITAL MOON TWIN - DATASET PIPELINE
====================================

Single master pipeline.

Run:
    python moon_dataset_pipeline.py

This script:
1. Processes the USGS/IAU lunar feature catalogue
2. Builds the mission/dataset catalogue
3. Builds the NASA LOLA RDR product catalogue
4. Builds the NASA LROC RDR product catalogue
5. Builds the source/provenance catalogue
6. Creates the scientific observation table
7. Creates the research database tables
8. Generates a dataset summary

Raw data inside 07_raw_data is never modified.
"""

from pathlib import Path
import csv
import sys
from datetime import date


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent

DOC_DIR = ROOT / "00_documentation"
FEATURE_DIR = ROOT / "01_feature_catalogue"
MISSION_DIR = ROOT / "02_missions"
DATASET_DIR = ROOT / "03_dataset_catalogue"
OBS_DIR = ROOT / "04_observations"
RESEARCH_DIR = ROOT / "05_research"
SOURCE_DIR = ROOT / "06_sources"
RAW_DIR = ROOT / "07_raw_data"
PROCESSED_DIR = ROOT / "08_processed_data"

USGS_DIR = RAW_DIR / "USGS"
NASA_DIR = RAW_DIR / "NASA"
ISRO_DIR = RAW_DIR / "ISRO"

LOLA_DIR = NASA_DIR / "LRO" / "LOLA"
LROC_DIR = NASA_DIR / "LRO" / "LROC"


# ============================================================
# GENERAL HELPERS
# ============================================================

def ensure_directories():
    directories = [
        DOC_DIR,
        FEATURE_DIR,
        MISSION_DIR,
        DATASET_DIR,
        OBS_DIR,
        RESEARCH_DIR,
        SOURCE_DIR,
        RAW_DIR,
        USGS_DIR,
        NASA_DIR,
        ISRO_DIR,
        PROCESSED_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=headers,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def read_csv(path):
    if not path.exists():
        return []

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        return list(csv.DictReader(f))


def count_csv_records(path):
    """
    Count actual CSV records, not physical lines.
    This handles CSV fields containing line breaks correctly.
    """

    if not path.exists():
        return 0

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        return sum(1 for _ in csv.DictReader(f))


def print_stage(number, title):
    print()
    print("=" * 70)
    print(f"STEP {number}: {title}")
    print("=" * 70)


# ============================================================
# STEP 1
# PROJECT STRUCTURE
# ============================================================

def validate_project():

    print_stage(1, "PROJECT STRUCTURE")

    ensure_directories()

    print("Project root:")
    print(ROOT)

    print("\nRequired directories checked/created.")

    directories = [
        FEATURE_DIR,
        DATASET_DIR,
        OBS_DIR,
        RESEARCH_DIR,
        SOURCE_DIR,
        RAW_DIR,
        PROCESSED_DIR,
    ]

    for directory in directories:

        status = "OK" if directory.exists() else "MISSING"

        print(
            f"  [{status}] "
            f"{directory.relative_to(ROOT)}"
        )


# ============================================================
# STEP 2
# USGS / IAU LUNAR FEATURES
# ============================================================

def process_features():

    print_stage(
        2,
        "USGS / IAU LUNAR FEATURE CATALOGUE"
    )

    output = (
        FEATURE_DIR /
        "lunar_features.csv"
    )

    shapefiles = list(
        USGS_DIR.rglob(
            "MOON_nomenclature_center_pts.shp"
        )
    )

    if not shapefiles:

        print(
            "ERROR: USGS lunar nomenclature "
            "shapefile not found."
        )

        print(
            "\nExpected location similar to:"
        )

        print(
            "07_raw_data/USGS/"
            "MOON_nomenclature/"
            "MOON_nomenclature_center_pts.shp"
        )

        return False

    shapefile = shapefiles[0]

    print("Found source:")
    print(f"  {shapefile}")

    try:
        import geopandas as gpd

    except ImportError:

        print(
            "\nERROR: GeoPandas is not installed."
        )

        print(
            "Install using:"
        )

        print(
            "pip install geopandas"
        )

        return False

    try:

        gdf = gpd.read_file(
            shapefile
        )

    except Exception as e:

        print(
            f"ERROR reading shapefile: {e}"
        )

        return False

    print(
        f"\nOfficial feature records found: "
        f"{len(gdf):,}"
    )

    headers = [
        "feature_id",
        "feature_name",
        "feature_type",
        "latitude",
        "longitude",
        "diameter_km",
        "north_latitude",
        "south_latitude",
        "east_longitude",
        "west_longitude",
        "hemisphere",
        "region",
        "parent_feature",
        "approval_status",
        "approval_date",
        "origin",
        "iau_reference",
        "source_id",
    ]

    rows = []

    for index, row in gdf.iterrows():

        latitude = row.get(
            "center_lat",
            ""
        )

        try:
            latitude_value = float(
                latitude
            )

        except (
            ValueError,
            TypeError
        ):

            latitude_value = None

        if latitude_value is None:

            hemisphere = ""

        elif latitude_value > 0:

            hemisphere = "Northern"

        elif latitude_value < 0:

            hemisphere = "Southern"

        else:

            hemisphere = "Equatorial"

        rows.append({

            "feature_id":
                f"LUN-{index + 1:07d}",

            "feature_name":
                row.get("name", ""),

            "feature_type":
                row.get("type", ""),

            "latitude":
                row.get("center_lat", ""),

            "longitude":
                row.get("center_lon", ""),

            "diameter_km":
                row.get("diameter", ""),

            "north_latitude":
                row.get("max_lat", ""),

            "south_latitude":
                row.get("min_lat", ""),

            "east_longitude":
                row.get("max_lon", ""),

            "west_longitude":
                row.get("min_lon", ""),

            "hemisphere":
                hemisphere,

            "region":
                row.get("quad_name", ""),

            "parent_feature":
                "",

            "approval_status":
                row.get("approval", ""),

            "approval_date":
                row.get("approvaldt", ""),

            "origin":
                row.get("origin", ""),

            "iau_reference":
                row.get("link", ""),

            "source_id":
                "USGS_IAU_MOON_GAZETTEER",
        })

    write_csv(
        output,
        headers,
        rows
    )

    print("\nOutput:")
    print(
        f"  {output.relative_to(ROOT)}"
    )

    print(
        f"Total lunar features: "
        f"{len(rows):,}"
    )

    print("\nFirst 3 features:")

    for row in rows[:3]:

        print(
            f"  {row['feature_id']} | "
            f"{row['feature_name']} | "
            f"{row['feature_type']}"
        )

    return True


# ============================================================
# STEP 3
# DATASET CATALOGUE
# ============================================================

def build_dataset_catalogue():

    print_stage(
        3,
        "DATASET CATALOGUE"
    )

    output = (
        DATASET_DIR /
        "dataset_catalogue.csv"
    )

    headers = [
        "dataset_id",
        "dataset_name",
        "agency",
        "mission",
        "instrument",
        "data_type",
        "description",
        "processing_level",
        "spatial_resolution",
        "temporal_resolution",
        "coverage",
        "format",
        "version",
        "release_date",
        "file_size",
        "source_url",
        "documentation_url",
        "citation",
    ]

    datasets = [

        # ====================================================
        # NASA LRO
        # ====================================================

        {
            "dataset_id": "NASA-LRO-LOLA",
            "dataset_name":
                "Lunar Orbiter Laser Altimeter",
            "agency": "NASA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument": "LOLA",
            "data_type":
                "Laser Altimetry / Topography",
            "description":
                "Lunar surface elevation and topographic measurements.",
            "processing_level": "RDR",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PDS",
            "version": "V1.0",
            "release_date": "2011-09-15",
            "file_size": "",
            "source_url":
                "https://pds.nasa.gov/",
            "documentation_url":
                "https://pds.nasa.gov/",
            "citation":
                "NASA LRO LOLA PDS dataset",
        },

        {
            "dataset_id": "NASA-LRO-LROC",
            "dataset_name":
                "Lunar Reconnaissance Orbiter Camera",
            "agency": "NASA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument": "LROC",
            "data_type":
                "Optical Imaging",
            "description":
                "High-resolution lunar surface imagery.",
            "processing_level": "RDR",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PDS",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pds.nasa.gov/",
            "documentation_url":
                "https://pds.nasa.gov/",
            "citation":
                "NASA LRO LROC PDS dataset",
        },

        {
            "dataset_id": "NASA-LRO-DIVINER",
            "dataset_name":
                "Diviner Lunar Radiometer",
            "agency": "NASA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument": "Diviner",
            "data_type":
                "Thermal Infrared",
            "description":
                "Lunar surface thermal measurements.",
            "processing_level": "RDR",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PDS",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pds.nasa.gov/",
            "documentation_url":
                "https://pds.nasa.gov/",
            "citation":
                "NASA LRO Diviner PDS dataset",
        },

        {
            "dataset_id": "NASA-LRO-LEND",
            "dataset_name":
                "Lunar Exploration Neutron Detector",
            "agency": "NASA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument": "LEND",
            "data_type":
                "Neutron / Hydrogen Measurements",
            "description":
                "Measurements related to lunar neutron flux and hydrogen abundance.",
            "processing_level": "RDR",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PDS",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pds.nasa.gov/",
            "documentation_url":
                "https://pds.nasa.gov/",
            "citation":
                "NASA LRO LEND PDS dataset",
        },

        {
            "dataset_id": "NASA-LRO-MINIRF",
            "dataset_name":
                "Mini-RF",
            "agency": "NASA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument": "Mini-RF",
            "data_type":
                "Radar / SAR",
            "description":
                "Synthetic aperture radar and polarimetric microwave observations.",
            "processing_level": "RDR",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PDS",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pds.nasa.gov/",
            "documentation_url":
                "https://pds.nasa.gov/",
            "citation":
                "NASA LRO Mini-RF PDS dataset",
        },

        # ====================================================
        # CHANDRAYAAN-2
        # ====================================================

        {
            "dataset_id": "ISRO-C2-CLASS",
            "dataset_name":
                "Chandrayaan-2 Large Area Soft X-ray Spectrometer",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "CLASS",
            "data_type":
                "X-ray Spectroscopy",
            "description":
                "Lunar elemental composition measurements using X-ray fluorescence.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 CLASS data",
        },

        {
            "dataset_id": "ISRO-C2-XSM",
            "dataset_name":
                "Chandrayaan-2 Solar X-ray Monitor",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "XSM",
            "data_type":
                "Solar X-ray",
            "description":
                "Solar X-ray observations supporting lunar elemental analysis.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon / Solar",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 XSM data",
        },

        {
            "dataset_id": "ISRO-C2-OHRC",
            "dataset_name":
                "Chandrayaan-2 Orbiter High Resolution Camera",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "OHRC",
            "data_type":
                "High Resolution Imaging",
            "description":
                "High-resolution optical observations of the lunar surface.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 OHRC data",
        },

        {
            "dataset_id": "ISRO-C2-TMC2",
            "dataset_name":
                "Chandrayaan-2 Terrain Mapping Camera-2",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "TMC-2",
            "data_type":
                "Terrain Mapping / Imaging",
            "description":
                "Stereo terrain mapping and lunar surface imaging.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 TMC-2 data",
        },

        {
            "dataset_id": "ISRO-C2-IIRS",
            "dataset_name":
                "Chandrayaan-2 Imaging Infrared Spectrometer",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "IIRS",
            "data_type":
                "Infrared Spectroscopy",
            "description":
                "Mineralogical and compositional observations of the lunar surface.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 IIRS data",
        },

        {
            "dataset_id": "ISRO-C2-SAR",
            "dataset_name":
                "Chandrayaan-2 Synthetic Aperture Radar",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "SAR",
            "data_type":
                "Radar",
            "description":
                "Radar observations of the lunar surface and subsurface.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 SAR data",
        },

        {
            "dataset_id": "ISRO-C2-CHACE2",
            "dataset_name":
                "Chandrayaan-2 Chandra's Atmospheric Composition Explorer-2",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "CHACE-2",
            "data_type":
                "Exosphere / Mass Spectrometry",
            "description":
                "Measurements of the lunar exosphere and tenuous atmospheric constituents.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon / Exosphere",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 CHACE-2 data",
        },

        {
            "dataset_id": "ISRO-C2-DFRS",
            "dataset_name":
                "Chandrayaan-2 Dual Frequency Radio Science",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-2",
            "instrument": "DFRS",
            "data_type":
                "Radio Science",
            "description":
                "Radio science observations associated with the Chandrayaan-2 mission.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage": "Moon",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch2/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch2/",
            "citation":
                "ISRO Chandrayaan-2 DFRS data",
        },

        # ====================================================
        # CHANDRAYAAN-3
        # ====================================================

        {
            "dataset_id": "ISRO-C3-APXS",
            "dataset_name":
                "Chandrayaan-3 Alpha Particle X-ray Spectrometer",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-3",
            "instrument": "APXS",
            "data_type":
                "Elemental Composition",
            "description":
                "In-situ elemental composition measurements of lunar soil.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage":
                "Lunar south polar region",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch3/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch3/",
            "citation":
                "ISRO Chandrayaan-3 APXS data",
        },

        {
            "dataset_id": "ISRO-C3-LIBS",
            "dataset_name":
                "Chandrayaan-3 Laser Induced Breakdown Spectroscope",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-3",
            "instrument": "LIBS",
            "data_type":
                "Elemental Composition",
            "description":
                "In-situ elemental composition measurements using laser spectroscopy.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage":
                "Lunar south polar region",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch3/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch3/",
            "citation":
                "ISRO Chandrayaan-3 LIBS data",
        },

        {
            "dataset_id": "ISRO-C3-CHASTE",
            "dataset_name":
                "Chandrayaan-3 ChaSTE",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-3",
            "instrument": "ChaSTE",
            "data_type":
                "Thermal Properties",
            "description":
                "Measurements of thermal properties of lunar soil.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage":
                "Lunar south polar region",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch3/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch3/",
            "citation":
                "ISRO Chandrayaan-3 ChaSTE data",
        },

        {
            "dataset_id": "ISRO-C3-ILSA",
            "dataset_name":
                "Chandrayaan-3 Instrument for Lunar Seismic Activity",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-3",
            "instrument": "ILSA",
            "data_type":
                "Seismic",
            "description":
                "Measurements of seismic activity near the Chandrayaan-3 landing site.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage":
                "Lunar south polar region",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch3/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch3/",
            "citation":
                "ISRO Chandrayaan-3 ILSA data",
        },

        {
            "dataset_id": "ISRO-C3-RAMBHA-LP",
            "dataset_name":
                "Chandrayaan-3 RAMBHA-LP",
            "agency": "ISRO",
            "mission":
                "Chandrayaan-3",
            "instrument": "RAMBHA-LP",
            "data_type":
                "Plasma / Electric Potential",
            "description":
                "Measurements of lunar near-surface plasma environment.",
            "processing_level": "",
            "spatial_resolution": "",
            "temporal_resolution": "",
            "coverage":
                "Lunar south polar region",
            "format": "PRADAN",
            "version": "",
            "release_date": "",
            "file_size": "",
            "source_url":
                "https://pradan.issdc.gov.in/ch3/",
            "documentation_url":
                "https://pradan.issdc.gov.in/ch3/",
            "citation":
                "ISRO Chandrayaan-3 RAMBHA-LP data",
        },
    ]

    write_csv(
        output,
        headers,
        datasets
    )

    print("Dataset catalogue created:")
    print(
        f"  {output.relative_to(ROOT)}"
    )

    print(
        f"Total datasets: {len(datasets)}"
    )

    print("\nNASA datasets:")
    print("  5")

    print("ISRO Chandrayaan-2 datasets:")
    print("  8")

    print("ISRO Chandrayaan-3 datasets:")
    print("  5")

    return True


# ============================================================
# STEP 4
# NASA LRO LOLA PRODUCT INVENTORY
# ============================================================

def build_lola_catalogue():

    print_stage(
        4,
        "NASA LRO LOLA PRODUCT INVENTORY"
    )

    source_index = (
        DATASET_DIR /
        "lola_product_index.csv"
    )

    output = (
        DATASET_DIR /
        "lola_rdr_catalogue.csv"
    )

    if not source_index.exists():

        print(
            "ERROR: LOLA product index not found:"
        )

        print(
            f"  {source_index.relative_to(ROOT)}"
        )

        raw_index = (
            LOLA_DIR /
            "rdrindex.tab"
        )

        if raw_index.exists():

            print(
                "\nRaw rdrindex.tab exists."
            )

            print(
                "The processed "
                "lola_product_index.csv "
                "is required."
            )

        else:

            print(
                "No LOLA index found."
            )

        return False

    rows = read_csv(
        source_index
    )

    print(
        f"LOLA index records: "
        f"{len(rows):,}"
    )

    headers = [
        "dataset_id",
        "instrument",
        "mission",
        "volume_id",
        "file_specification_name",
        "mission_phase_name",
        "target_name",
        "product_id",
        "product_version_id",
        "product_creation_time",
        "data_set_id",
        "standard_data_product_id",
        "start_time",
        "stop_time",
        "spacecraft_clock_start_count",
        "spacecraft_clock_stop_count",
    ]

    rdr_rows = []

    for row in rows:

        # IMPORTANT:
        # lola_product_index.csv uses LOWERCASE
        # column names.

        dataset_id = str(
            row.get(
                "data_set_id",
                ""
            )
        ).strip().upper()

        # Select only the official
        # LOLA 3 RDR dataset.
        if dataset_id != (
            "LRO-L-LOLA-3-RDR-V1.0"
        ):
            continue

        rdr_rows.append({

            "dataset_id":
                "NASA-LRO-LOLA",

            "instrument":
                "LOLA",

            "mission":
                "Lunar Reconnaissance Orbiter",

            "volume_id":
                row.get(
                    "volume_id",
                    ""
                ),

            "file_specification_name":
                row.get(
                    "file_specification_name",
                    ""
                ),

            "mission_phase_name":
                row.get(
                    "mission_phase_name",
                    ""
                ),

            "target_name":
                row.get(
                    "target_name",
                    ""
                ),

            "product_id":
                row.get(
                    "product_id",
                    ""
                ),

            "product_version_id":
                row.get(
                    "product_version_id",
                    ""
                ),

            "product_creation_time":
                row.get(
                    "product_creation_time",
                    ""
                ),

            "data_set_id":
                row.get(
                    "data_set_id",
                    ""
                ),

            "standard_data_product_id":
                row.get(
                    "standard_data_product_id",
                    ""
                ),

            "start_time":
                row.get(
                    "start_time",
                    ""
                ),

            "stop_time":
                row.get(
                    "stop_time",
                    ""
                ),

            "spacecraft_clock_start_count":
                row.get(
                    "spacecraft_clock_start_count",
                    ""
                ),

            "spacecraft_clock_stop_count":
                row.get(
                    "spacecraft_clock_stop_count",
                    ""
                ),
        })

    write_csv(
        output,
        headers,
        rdr_rows
    )

    print(
        f"LOLA RDR products: "
        f"{len(rdr_rows):,}"
    )

    print("Output:")
    print(
        f"  {output.relative_to(ROOT)}"
    )

    if rdr_rows:

        print("\nExample product:")

        example = rdr_rows[0]

        print(
            f"  Product ID : "
            f"{example['product_id']}"
        )

        print(
            f"  Dataset    : "
            f"{example['data_set_id']}"
        )

        print(
            f"  Start      : "
            f"{example['start_time']}"
        )

        print(
            f"  Stop       : "
            f"{example['stop_time']}"
        )

    return True


# ============================================================
# STEP 9
# NASA LRO LROC PRODUCT CATALOGUE
# ============================================================

def build_lroc_catalogue():

    print_stage(
        9,
        "NASA LRO LROC PRODUCT CATALOGUE"
    )

    index_file = LROC_DIR / "INDEX.TAB"
    label_file = LROC_DIR / "INDEX.LBL"
    output = DATASET_DIR / "lroc_rdr_catalogue.csv"

    if not index_file.exists():
        print("ERROR: LROC INDEX.TAB not found:")
        print(f"  {index_file.relative_to(ROOT)}")
        return False

    if not label_file.exists():
        print("ERROR: LROC INDEX.LBL not found:")
        print(f"  {label_file.relative_to(ROOT)}")
        return False

    # IMPORTANT:
    # The LROC PDS3 INDEX.TAB is an ASCII interchange table whose
    # records are comma-delimited and contain quoted text fields.
    # ROW_BYTES = 2724 describes the fixed record width, but the
    # scientific fields must be parsed as CSV so that commas inside
    # quoted DESCRIPTION/RATIONALE fields are handled correctly.
    source_columns = [
        "data_set_id",
        "volume_id",
        "file_specification_name",
        "instrument_host_id",
        "product_id",
        "product_version_id",
        "target_name",
        "rationale_desc",
        "software_name",
        "product_creation_time",
        "lines",
        "line_samples",
        "sample_bits",
        "bands",
        "map_projection_type",
        "projection_latitude_type",
        "coordinate_system_name",
        "positive_longitude_direction",
        "center_longitude",
        "center_latitude",
        "map_resolution",
        "map_scale",
        "maximum_latitude",
        "minimum_latitude",
        "easternmost_longitude",
        "westernmost_longitude",
        "description",
    ]

    headers = [
        "dataset_id",
        "instrument",
        "mission",
    ] + source_columns

    rows = []
    malformed = 0
    physical_records = 0

    with open(
        index_file,
        "r",
        encoding="ascii",
        errors="replace",
        newline=""
    ) as f:
        reader = csv.reader(f)

        for record in reader:
            if not record or not any(field.strip() for field in record):
                continue

            physical_records += 1

            if len(record) != len(source_columns):
                malformed += 1
                continue

            cleaned = [field.strip() for field in record]
            row = dict(zip(source_columns, cleaned))

            rows.append({
                "dataset_id": "NASA-LRO-LROC",
                "instrument": "LROC",
                "mission": "Lunar Reconnaissance Orbiter",
                **row,
            })

    print(f"LROC INDEX.TAB records read: {physical_records:,}")
    print(f"LROC INDEX.TAB records parsed: {len(rows):,}")

    if malformed:
        print(f"Skipped malformed records: {malformed:,}")
    else:
        print("Skipped malformed records: 0")

    write_csv(
        output,
        headers,
        rows
    )

    print(f"LROC RDR products: {len(rows):,}")
    print("Output:")
    print(f"  {output.relative_to(ROOT)}")

    if rows:
        example = rows[0]
        print("\nExample product:")
        print(f"  Product ID : {example['product_id']}")
        print(f"  Dataset    : {example['data_set_id']}")
        print(
            f"  Center     : {example['center_latitude']}, "
            f"{example['center_longitude']}"
        )
        print(f"  Map scale  : {example['map_scale']}")

    return True


# ============================================================
# STEP 5
# SOURCES / PROVENANCE
# ============================================================

def build_sources():

    print_stage(
        5,
        "SOURCE / PROVENANCE CATALOGUE"
    )

    output = (
        SOURCE_DIR /
        "sources.csv"
    )

    headers = [
        "source_id",
        "agency",
        "organization",
        "mission",
        "instrument",
        "dataset_id",
        "product_id",
        "title",
        "url",
        "version",
        "release_date",
        "access_date",
        "citation",
    ]

    today = date.today().isoformat()

    sources = [

        {
            "source_id":
                "USGS_IAU_MOON_GAZETTEER",
            "agency":
                "USGS / IAU",
            "organization":
                "USGS Astrogeology / IAU",
            "mission": "",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "Gazetteer of Planetary Nomenclature - Moon",
            "url":
                "https://planetarynames.wr.usgs.gov/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "IAU Working Group for Planetary System Nomenclature / USGS",
        },

        {
            "source_id":
                "NASA_PDS",
            "agency":
                "NASA",
            "organization":
                "NASA Planetary Data System",
            "mission": "",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "NASA Planetary Data System",
            "url":
                "https://pds.nasa.gov/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "NASA Planetary Data System",
        },

        {
            "source_id":
                "NASA_LRO_LOLA",
            "agency":
                "NASA",
            "organization":
                "NASA Goddard Space Flight Center / LRO LOLA",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument":
                "LOLA",
            "dataset_id":
                "NASA-LRO-LOLA",
            "product_id": "",
            "title":
                "LRO Moon Laser Altimeter RDR",
            "url":
                "https://pds-geosciences.wustl.edu/",
            "version":
                "LRO-L-LOLA-3-RDR-V1.0",
            "release_date":
                "2011-09-15",
            "access_date": today,
            "citation":
                "NASA LRO LOLA PDS dataset",
        },

        {
            "source_id":
                "NASA_LRO_LROC",
            "agency":
                "NASA",
            "organization":
                "NASA / LRO Camera Science Team",
            "mission":
                "Lunar Reconnaissance Orbiter",
            "instrument":
                "LROC",
            "dataset_id":
                "NASA-LRO-LROC",
            "product_id": "",
            "title":
                "LRO Lunar Reconnaissance Orbiter Camera RDR",
            "url":
                "https://pds-imaging.jpl.nasa.gov/",
            "version":
                "LRO-L-LROC-5-RDR-V1.0",
            "release_date": "",
            "access_date": today,
            "citation":
                "NASA LRO LROC / Planetary Data System",
        },

        {
            "source_id":
                "ISRO_PRADAN",
            "agency":
                "ISRO",
            "organization":
                "Indian Space Research Organisation / ISSDC",
            "mission": "",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "Planetary Data Archive - PRADAN",
            "url":
                "https://pradan.issdc.gov.in/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "ISRO Science Data Archive",
        },

        {
            "source_id":
                "ISRO_CHANDRAYAAN2",
            "agency":
                "ISRO",
            "organization":
                "ISSDC",
            "mission":
                "Chandrayaan-2",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "Chandrayaan-2 Science Data Archive",
            "url":
                "https://pradan.issdc.gov.in/ch2/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "ISRO Chandrayaan-2 PRADAN",
        },

        {
            "source_id":
                "ISRO_CHANDRAYAAN3",
            "agency":
                "ISRO",
            "organization":
                "ISSDC",
            "mission":
                "Chandrayaan-3",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "Chandrayaan-3 Science Data Archive",
            "url":
                "https://pradan.issdc.gov.in/ch3/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "ISRO Chandrayaan-3 PRADAN",
        },

        {
            "source_id":
                "USGS_LUNAR_GEOLOGY",
            "agency":
                "USGS",
            "organization":
                "USGS Astrogeology Science Center",
            "mission": "",
            "instrument": "",
            "dataset_id": "",
            "product_id": "",
            "title":
                "Unified Geologic Map of the Moon",
            "url":
                "https://astrogeology.usgs.gov/",
            "version": "",
            "release_date": "",
            "access_date": today,
            "citation":
                "USGS Unified Geologic Map of the Moon",
        },
    ]

    write_csv(
        output,
        headers,
        sources
    )

    print(
        f"Sources created: "
        f"{len(sources)}"
    )

    print("Output:")
    print(
        f"  {output.relative_to(ROOT)}"
    )

    return True

# ============================================================
# STEP 6
# SCIENTIFIC OBSERVATIONS
# ============================================================

def build_observations():
    """
    Build the standardized observation table from verified scientific data.

    Current implemented scientific source:
      NASA LRO LOLA RDR -> rdr2csv-converted CSV.

    The converted LOLA CSV contains one shot per row and up to five
    detector spots (D1-D5). Source values are preserved without
    relabeling the scientific meaning of the source fields.
    """

    print_stage(
        6,
        "OBSERVATION DATABASE"
    )

    output = (
        OBS_DIR /
        "lunar_observations.csv"
    )

    headers = [
        "observation_id",
        "feature_id",
        "mission",
        "instrument",
        "dataset_id",
        "product_id",
        "observation_type",
        "parameter",
        "value",
        "unit",
        "latitude",
        "longitude",
        "observation_time",
        "processing_level",
        "source_id",
    ]

    lola_csv_candidates = [
        PROCESSED_DIR / "LOLA_091940157.csv",
        LOLA_DIR / "lola_rdr_software" / "Windows_bin" /
        "LOLA_091940157.csv",
        LOLA_DIR / "lola_rdr_software" / "Windows_bin" /
        "LOLARDR_091940157.csv",
        LOLA_DIR / "LOLARDR_091940157.csv",
    ]

    lola_csv = next(
        (path for path in lola_csv_candidates if path.exists()),
        None
    )

    if lola_csv is None:
        print("LOLA converted CSV not found.")
        print("Expected preferred location:")
        print(
            f"  {PROCESSED_DIR.relative_to(ROOT)}"
            "/LOLA_091940157.csv"
        )

        write_csv(output, headers, [])
        print("Observation table initialized with 0 verified observations.")
        print("Output:")
        print(f"  {output.relative_to(ROOT)}")
        return True

    print("Verified LOLA CSV found:")
    print(f"  {lola_csv.relative_to(ROOT)}")

    observations = []
    record_count = 0
    valid_spot_count = 0
    skipped_rows = 0

    try:
        with open(
            lola_csv,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as f:
            # rdr2csv pads some column names with leading spaces.
            # Read the header separately and normalize it before
            # constructing the DictReader.
            raw_header = next(csv.reader(f))

            normalized_header = [
                name.strip() if name else name
                for name in raw_header
            ]

            reader = csv.DictReader(
                f,
                fieldnames=normalized_header
            )

            required_columns = {
                "Coordinated_Universal_Time",
                "D1_Longitude",
                "D1_Latitude",
                "D1_Radius",
            }

            if not required_columns.issubset(
                set(normalized_header)
            ):
                print(
                    "ERROR: LOLA CSV does not contain the expected "
                    "scientific columns."
                )
                print(
                    "Expected at least: "
                    "Coordinated_Universal_Time, "
                    "D1_Longitude, D1_Latitude, D1_Radius"
                )
                return False

            for row in reader:
                record_count += 1

                timestamp = (
                    row.get(
                        "Coordinated_Universal_Time",
                        ""
                    ) or ""
                ).strip()

                # rdr2csv uses D1-D5 for the five LOLA spots.
                for spot_number in range(1, 6):
                    lon_key = f"D{spot_number}_Longitude"
                    lat_key = f"D{spot_number}_Latitude"
                    radius_key = f"D{spot_number}_Radius"

                    lon_text = (
                        row.get(lon_key, "") or ""
                    ).strip()
                    lat_text = (
                        row.get(lat_key, "") or ""
                    ).strip()
                    radius_text = (
                        row.get(radius_key, "") or ""
                    ).strip()

                    if not lon_text or not lat_text or not radius_text:
                        continue

                    try:
                        longitude = float(lon_text)
                        latitude = float(lat_text)
                        radius = float(radius_text)
                    except (ValueError, TypeError):
                        skipped_rows += 1
                        continue

                    # LOLA uses -99 for unavailable spot measurements.
                    if (
                        radius <= -98.0
                        or longitude <= -98.0
                        or latitude <= -98.0
                    ):
                        continue

                    if not (-90.0 <= latitude <= 90.0):
                        skipped_rows += 1
                        continue

                    if not (-360.0 <= longitude <= 360.0):
                        skipped_rows += 1
                        continue

                    valid_spot_count += 1

                    observations.append({
                        "observation_id":
                            f"LOLA-091940157-{record_count:06d}-D{spot_number}",
                        "feature_id": "",
                        "mission":
                            "Lunar Reconnaissance Orbiter",
                        "instrument": "LOLA",
                        "dataset_id":
                            "LRO-L-LOLA-3-RDR-V1.0",
                        "product_id":
                            "LOLARDR_091940157_DAT",
                        "observation_type":
                            "topography",
                        "parameter":
                            "spot_radius",
                        "value":
                            radius,
                        "unit":
                            "m",
                        "latitude":
                            latitude,
                        "longitude":
                            longitude,
                        "observation_time":
                            timestamp,
                        "processing_level":
                            "RDR",
                        "source_id":
                            "NASA_LRO_LOLA",
                    })

    except Exception as e:
        print(f"ERROR reading LOLA CSV: {e}")
        return False

    write_csv(
        output,
        headers,
        observations
    )

    print()
    print(f"LOLA source records read: {record_count:,}")
    print(f"Valid LOLA spot observations: {valid_spot_count:,}")
    print(f"Skipped invalid/unusable fields: {skipped_rows:,}")

    print("Important:")
    print(
        "  feature_id is left blank because this product does not "
        "provide an explicit IAU feature association."
    )
    print(
        "  The LOLA source D1-D5_Radius field is preserved as "
        "spot_radius without relabeling it as elevation."
    )

    print("Output:")
    print(
        f"  {output.relative_to(ROOT)}"
    )

    return True

# ============================================================
# STEP 7
# RESEARCH DATABASE
# ============================================================

def build_research():

    print_stage(
        7,
        "RESEARCH DATABASE"
    )

    papers_output = (
        RESEARCH_DIR /
        "research_papers.csv"
    )

    findings_output = (
        RESEARCH_DIR /
        "research_findings.csv"
    )

    papers_headers = [
        "paper_id",
        "title",
        "authors",
        "year",
        "journal",
        "doi",
        "abstract",
        "keywords",
        "mission",
        "instrument",
        "region",
        "source_url",
    ]

    findings_headers = [
        "finding_id",
        "paper_id",
        "region_id",
        "finding_type",
        "observation",
        "finding",
        "interpretation",
        "limitations",
        "related_dataset",
    ]

    # Verified research records selected from primary journal pages and
    # official ISRO/ISSDC research documentation.  The text below is a
    # concise structured summary, not a replacement for the papers.
    verified_papers = [
        {
            "paper_id": "PAPER-LOLA-001",
            "title": "Initial observations from the Lunar Orbiter Laser Altimeter (LOLA)",
            "authors": "Smith et al.",
            "year": "2010",
            "journal": "Geophysical Research Letters",
            "doi": "10.1029/2010GL043751",
            "abstract": "Describes early LOLA measurements, the global lunar topographic model, geodetic accuracy, slope and roughness products, and polar topography. The study reports more than 2.0 billion elevation measurements by June 2010 and describes the use of LOLA ranges to determine lunar radius and topography.",
            "keywords": "LOLA; lunar topography; elevation; geodesy; polar regions; roughness",
            "mission": "Lunar Reconnaissance Orbiter",
            "instrument": "LOLA",
            "region": "Global Moon; lunar polar regions",
            "source_url": "https://doi.org/10.1029/2010GL043751",
        },
        {
            "paper_id": "PAPER-LOLA-002",
            "title": "Lunar impact basins: Stratigraphy, sequence and ages from superposed impact crater populations measured from Lunar Orbiter Laser Altimeter (LOLA) data",
            "authors": "Fassett et al.",
            "year": "2012",
            "journal": "Journal of Geophysical Research: Planets",
            "doi": "10.1029/2011JE003951",
            "abstract": "Uses LOLA topography to measure superposed impact-crater populations for 30 lunar basins with diameters of at least 300 km, supporting analysis of basin stratigraphy, sequence and relative ages.",
            "keywords": "impact basins; craters; stratigraphy; chronology; LOLA; topography",
            "mission": "Lunar Reconnaissance Orbiter",
            "instrument": "LOLA",
            "region": "30 large lunar impact basins",
            "source_url": "https://doi.org/10.1029/2011JE003951",
        },
        {
            "paper_id": "PAPER-LOLA-003",
            "title": "The transition from complex craters to multi-ring basins on the Moon: Quantitative geometric properties from Lunar Reconnaissance Orbiter Lunar Orbiter Laser Altimeter (LOLA) data",
            "authors": "Baker et al.",
            "year": "2012",
            "journal": "Journal of Geophysical Research: Planets",
            "doi": "10.1029/2011JE004021",
            "abstract": "Uses LOLA topography to quantify the morphology and geometry of lunar impact basins across the transition from complex craters to peak-ring and multi-ring basins.",
            "keywords": "impact craters; impact basins; morphology; morphometry; LOLA",
            "mission": "Lunar Reconnaissance Orbiter",
            "instrument": "LOLA",
            "region": "Large lunar impact basins",
            "source_url": "https://doi.org/10.1029/2011JE004021",
        },
        {
            "paper_id": "PAPER-LOLA-004",
            "title": "The global albedo of the Moon at 1064 nm from LOLA",
            "authors": "Lucey et al.",
            "year": "2014",
            "journal": "Journal of Geophysical Research: Planets",
            "doi": "10.1002/2013JE004592",
            "abstract": "Uses LOLA 1064-nm reflectance measurements to characterize global lunar albedo and discusses anomalous reflectance in polar crater environments, including Shackleton crater.",
            "keywords": "LOLA; albedo; reflectance; Shackleton; polar regions; nanophase iron",
            "mission": "Lunar Reconnaissance Orbiter",
            "instrument": "LOLA",
            "region": "Global Moon; Shackleton crater; south polar region",
            "source_url": "https://doi.org/10.1002/2013JE004592",
        },
        {
            "paper_id": "PAPER-CH2-001",
            "title": "Chandrayaan-2 Large Area Soft X-ray Spectrometer (CLASS): Calibration, In-flight performance and first results",
            "authors": "Pillai et al.",
            "year": "2021",
            "journal": "Icarus",
            "doi": "10.1016/j.icarus.2021.114436",
            "abstract": "Presents CLASS calibration, in-flight performance and elemental-abundance measurements derived from lunar X-ray fluorescence. The study demonstrates mapping capability for O, Mg, Al and Si and localized measurements of Ca, Ti and Fe.",
            "keywords": "CLASS; X-ray fluorescence; elemental abundance; Moon; Chandrayaan-2",
            "mission": "Chandrayaan-2",
            "instrument": "CLASS",
            "region": "Mare Imbrium; farside highlands; nearside western mare",
            "source_url": "https://doi.org/10.1016/j.icarus.2021.114436",
        },
        {
            "paper_id": "PAPER-CH2-002",
            "title": "L- and S-band Polarimetric Synthetic Aperture Radar on Chandrayaan-2 Mission",
            "authors": "Putrevu et al.",
            "year": "2020",
            "journal": "Current Science",
            "doi": "10.18520/cs/v118/i2/226-233",
            "abstract": "Describes the Chandrayaan-2 dual-frequency polarimetric SAR payload using L- and S-band observations, including its intended application to lunar polar mapping and characterization of permanently shadowed regions and possible water ice.",
            "keywords": "DFSAR; SAR; L-band; S-band; polarimetry; permanently shadowed regions; water ice",
            "mission": "Chandrayaan-2",
            "instrument": "DFSAR",
            "region": "Lunar polar regions; permanently shadowed regions",
            "source_url": "https://doi.org/10.18520/cs/v118/i2/226-233",
        },
        {
            "paper_id": "PAPER-CH2-003",
            "title": "Imaging Infrared Spectrometer onboard Chandrayaan-2 Orbiter",
            "authors": "Chowdhury et al.",
            "year": "2020",
            "journal": "Current Science",
            "doi": "10.18520/cs/v118/i3/368-375",
            "abstract": "Describes the Chandrayaan-2 IIRS imaging hyperspectral instrument for lunar mineralogical investigation, covering approximately 0.8–5.0 micrometres with 256 contiguous spectral bands.",
            "keywords": "IIRS; hyperspectral imaging; mineralogy; spectroscopy; Chandrayaan-2",
            "mission": "Chandrayaan-2",
            "instrument": "IIRS",
            "region": "Moon; polar regions",
            "source_url": "https://doi.org/10.18520/cs/v118/i3/368-375",
        },
        {
            "paper_id": "PAPER-CH3-001",
            "title": "Chandrayaan-3 APXS elemental abundance measurements at lunar high latitude",
            "authors": "Vadawale et al.",
            "year": "2024",
            "journal": "Nature",
            "doi": "10.1038/s41586-024-07870-7",
            "abstract": "Reports 23 in-situ APXS measurements near the Chandrayaan-3 landing site. The study describes fairly uniform local composition dominated by ferroan anorthosite and reports relatively higher magnesium with respect to calcium, indicating mixing of additional mafic material.",
            "keywords": "APXS; elemental abundance; ferroan anorthosite; lunar highlands; Chandrayaan-3",
            "mission": "Chandrayaan-3",
            "instrument": "APXS",
            "region": "Chandrayaan-3 landing site; lunar southern high latitudes",
            "source_url": "https://doi.org/10.1038/s41586-024-07870-7",
        },
        {
            "paper_id": "PAPER-CH3-002",
            "title": "Primitive lunar mantle materials at the Chandrayaan-3 landing site",
            "authors": "Patel et al.",
            "year": "2025",
            "journal": "Communications Earth & Environment",
            "doi": "10.1038/s43247-025-02305-1",
            "abstract": "Assesses APXS measurements of sodium, potassium and sulfur at the Chandrayaan-3 highland landing site and compares them with other lunar highland measurements to investigate compositional relationships and possible primitive mantle contributions.",
            "keywords": "APXS; sodium; potassium; sulfur; lunar mantle; South Pole-Aitken; Chandrayaan-3",
            "mission": "Chandrayaan-3",
            "instrument": "APXS",
            "region": "Chandrayaan-3 landing site; southern highland; South Pole-Aitken-related terrain",
            "source_url": "https://doi.org/10.1038/s43247-025-02305-1",
        },
    ]

    verified_findings = [
        {
            "finding_id": "FIND-LOLA-001",
            "paper_id": "PAPER-LOLA-001",
            "region_id": "",
            "finding_type": "topography",
            "observation": "LOLA provides dense global laser-ranging measurements and high-resolution polar topography.",
            "finding": "The study reports a high-resolution global lunar topographic model and improved geodetic characterization.",
            "interpretation": "LOLA measurements support precise lunar elevation, geodesy, slope, roughness and polar illumination studies.",
            "limitations": "This is an early-mission results paper and does not represent the full later LOLA archive.",
            "related_dataset": "NASA-LRO-LOLA",
        },
        {
            "finding_id": "FIND-LOLA-002",
            "paper_id": "PAPER-LOLA-002",
            "region_id": "",
            "finding_type": "impact_basin_chronology",
            "observation": "LOLA topography was used to measure superposed crater populations across 30 large basins.",
            "finding": "The crater populations were used to investigate basin stratigraphy, sequence and relative ages.",
            "interpretation": "Quantitative topography enables comparative study of the Moon's large impact-basin history.",
            "limitations": "The analysis is focused on selected large basins rather than every lunar named feature.",
            "related_dataset": "NASA-LRO-LOLA",
        },
        {
            "finding_id": "FIND-LOLA-003",
            "paper_id": "PAPER-LOLA-003",
            "region_id": "",
            "finding_type": "morphometry",
            "observation": "LOLA topography provides quantitative measurements of large impact-basin geometry.",
            "finding": "The study characterizes geometric trends across complex craters, peak-ring basins and multi-ring basins.",
            "interpretation": "High-density topography improves quantitative comparison of impact structures.",
            "limitations": "The conclusions concern large impact structures and are not a classification of all lunar craters.",
            "related_dataset": "NASA-LRO-LOLA",
        },
        {
            "finding_id": "FIND-LOLA-004",
            "paper_id": "PAPER-LOLA-004",
            "region_id": "",
            "finding_type": "reflectance",
            "observation": "LOLA measures 1064-nm reflected laser energy in addition to ranging information.",
            "finding": "The global albedo analysis identifies unusual reflectance characteristics in some polar crater environments, including Shackleton.",
            "interpretation": "LOLA reflectance can be combined with topography and illumination context when studying polar surface properties.",
            "limitations": "Reflectance anomalies have multiple possible explanations and are not by themselves direct measurements of surface ice abundance.",
            "related_dataset": "NASA-LRO-LOLA",
        },
        {
            "finding_id": "FIND-CH2-001",
            "paper_id": "PAPER-CH2-001",
            "region_id": "",
            "finding_type": "elemental_composition",
            "observation": "CLASS measures lunar X-ray fluorescence spectra remotely from lunar orbit.",
            "finding": "The study demonstrates calibrated elemental-abundance measurements for farside highland and nearside mare regions and maps major elements at kilometre-scale spatial resolution.",
            "interpretation": "CLASS provides direct X-ray-fluorescence constraints on lunar surface elemental composition.",
            "limitations": "Elemental retrieval depends on solar X-ray conditions, calibration and spectral modelling.",
            "related_dataset": "ISRO-C2-CLASS",
        },
        {
            "finding_id": "FIND-CH2-002",
            "paper_id": "PAPER-CH2-002",
            "region_id": "",
            "finding_type": "radar",
            "observation": "Chandrayaan-2 DFSAR combines L- and S-band polarimetric SAR observations.",
            "finding": "The instrument is designed for high-resolution polar mapping and characterization of permanently shadowed regions, including investigation of possible water ice signatures.",
            "interpretation": "Dual-frequency polarimetric radar provides complementary information to optical and thermal observations in shadowed terrain.",
            "limitations": "Radar signatures are not equivalent to a direct measurement of water-ice abundance; interpretation depends on scattering models and ancillary data.",
            "related_dataset": "ISRO-C2-SAR",
        },
        {
            "finding_id": "FIND-CH2-003",
            "paper_id": "PAPER-CH2-003",
            "region_id": "",
            "finding_type": "mineralogy",
            "observation": "IIRS acquires hyperspectral observations from approximately 0.8 to 5.0 micrometres using 256 contiguous bands.",
            "finding": "The instrument provides a dataset for mapping and studying lunar mineralogical and hydroxyl-related spectral characteristics.",
            "interpretation": "Hyperspectral measurements provide spectral constraints that complement morphology and elemental observations.",
            "limitations": "Mineralogical interpretation depends on calibration, spectral modelling and comparison with laboratory or established lunar spectra.",
            "related_dataset": "ISRO-C2-IIRS",
        },
        {
            "finding_id": "FIND-CH3-001",
            "paper_id": "PAPER-CH3-001",
            "region_id": "",
            "finding_type": "elemental_composition",
            "observation": "APXS acquired 23 in-situ measurements near the Chandrayaan-3 landing site.",
            "finding": "The local terrain was reported as fairly uniform and primarily ferroan anorthosite, with relatively higher magnesium compared with calcium suggesting additional mafic material.",
            "interpretation": "The measurements provide ground truth for remote-sensing observations of the lunar southern high-latitude highland environment.",
            "limitations": "The measurements cover a small local area around the landing site and should not be generalized to the entire lunar south polar region.",
            "related_dataset": "ISRO-C3-APXS",
        },
        {
            "finding_id": "FIND-CH3-002",
            "paper_id": "PAPER-CH3-002",
            "region_id": "",
            "finding_type": "geochemistry",
            "observation": "APXS measurements at the Chandrayaan-3 landing site were compared with other lunar highland compositions for Na, K and S.",
            "finding": "The study reports depletion in sodium and potassium and enrichment in sulfur relative to comparison highland sites.",
            "interpretation": "The authors relate the composition to material associated with ancient lunar crustal and South Pole-Aitken processes and discuss possible primitive mantle contributions.",
            "limitations": "The interpretation is model-dependent and is tied to comparison datasets and geological context.",
            "related_dataset": "ISRO-C3-APXS",
        },
    ]

    existing_papers = read_csv(
        papers_output
    )

    existing_findings = read_csv(
        findings_output
    )

    if existing_papers:
        print(
            f"Existing research papers preserved: "
            f"{len(existing_papers):,}"
        )
    else:
        write_csv(
            papers_output,
            papers_headers,
            verified_papers
        )
        print(
            f"Verified research papers added: "
            f"{len(verified_papers):,}"
        )

    if existing_findings:
        print(
            f"Existing research findings preserved: "
            f"{len(existing_findings):,}"
        )
    else:
        write_csv(
            findings_output,
            findings_headers,
            verified_findings
        )
        print(
            f"Verified research findings added: "
            f"{len(verified_findings):,}"
        )

    print("Outputs:")
    print(
        f"  {papers_output.relative_to(ROOT)}"
    )
    print(
        f"  {findings_output.relative_to(ROOT)}"
    )

    return True


# ============================================================
# STEP 11
# LROC / IAU FEATURE SPATIAL LINKS
# ============================================================

def build_lroc_feature_links():
    """
    Build documented spatial links between LROC RDR product centers
    and USGS/IAU lunar feature bounding boxes.

    A link means the LROC product center falls inside the official
    feature bounding box. It does NOT claim that the product image
    observes the named feature itself.

    Longitude values are compared modulo 360 degrees so equivalent
    longitude representations can be matched.
    """

    print_stage(
        11,
        "LROC / IAU FEATURE SPATIAL LINKS"
    )

    lroc_file = DATASET_DIR / "lroc_rdr_catalogue.csv"
    feature_file = FEATURE_DIR / "lunar_features.csv"
    output = PROCESSED_DIR / "lroc_feature_spatial_links.csv"

    if not lroc_file.exists():
        print("ERROR: LROC catalogue not found:")
        print(f"  {lroc_file.relative_to(ROOT)}")
        return False

    if not feature_file.exists():
        print("ERROR: lunar feature catalogue not found:")
        print(f"  {feature_file.relative_to(ROOT)}")
        return False

    lroc_rows = read_csv(lroc_file)
    feature_rows = read_csv(feature_file)

    print(f"LROC products read: {len(lroc_rows):,}")
    print(f"Lunar features read: {len(feature_rows):,}")

    headers = [
        "product_id",
        "feature_id",
        "feature_name",
        "feature_type",
        "product_center_latitude",
        "product_center_longitude",
        "feature_latitude",
        "feature_longitude",
        "feature_north_latitude",
        "feature_south_latitude",
        "feature_east_longitude",
        "feature_west_longitude",
        "relationship",
        "source_id",
    ]

    # Index features by integer latitude bins. This avoids comparing
    # every LROC product against all 9,087 features.
    latitude_index = {}
    valid_features = 0

    for feature in feature_rows:
        try:
            south = float(feature.get("south_latitude", ""))
            north = float(feature.get("north_latitude", ""))
        except (ValueError, TypeError):
            continue

        if south > north:
            south, north = north, south

        south = max(-90.0, south)
        north = min(90.0, north)

        if south > north:
            continue

        south_bin = int(south)
        north_bin = int(north)

        for latitude_bin in range(south_bin, north_bin + 1):
            latitude_index.setdefault(latitude_bin, []).append(feature)

        valid_features += 1

    print(
        f"Features with usable latitude bounds: "
        f"{valid_features:,}"
    )

    links = []
    skipped_products = 0

    for product in lroc_rows:
        product_id = (
            product.get("product_id", "") or ""
        ).strip()

        try:
            product_lat = float(
                product.get("center_latitude", "")
            )
            product_lon = float(
                product.get("center_longitude", "")
            )
        except (ValueError, TypeError):
            skipped_products += 1
            continue

        if not (-90.0 <= product_lat <= 90.0):
            skipped_products += 1
            continue

        product_lon_360 = product_lon % 360.0
        latitude_bin = int(product_lat)

        for feature in latitude_index.get(latitude_bin, []):
            try:
                south = float(
                    feature.get("south_latitude", "")
                )
                north = float(
                    feature.get("north_latitude", "")
                )
                west = float(
                    feature.get("west_longitude", "")
                )
                east = float(
                    feature.get("east_longitude", "")
                )
            except (ValueError, TypeError):
                continue

            if south > north:
                south, north = north, south

            if not (south <= product_lat <= north):
                continue

            west_360 = west % 360.0
            east_360 = east % 360.0

            if west_360 <= east_360:
                longitude_match = (
                    west_360 <= product_lon_360 <= east_360
                )
            else:
                # Feature bounding box crosses the 0/360 boundary.
                longitude_match = (
                    product_lon_360 >= west_360
                    or product_lon_360 <= east_360
                )

            if not longitude_match:
                continue

            links.append({
                "product_id": product_id,
                "feature_id": feature.get("feature_id", ""),
                "feature_name": feature.get("feature_name", ""),
                "feature_type": feature.get("feature_type", ""),
                "product_center_latitude": product_lat,
                "product_center_longitude": product_lon,
                "feature_latitude": feature.get("latitude", ""),
                "feature_longitude": feature.get("longitude", ""),
                "feature_north_latitude": feature.get("north_latitude", ""),
                "feature_south_latitude": feature.get("south_latitude", ""),
                "feature_east_longitude": feature.get("east_longitude", ""),
                "feature_west_longitude": feature.get("west_longitude", ""),
                "relationship": "center_inside_feature_bounds",
                "source_id": "USGS_IAU_MOON_GAZETTEER",
            })

    write_csv(output, headers, links)

    print()
    print(f"Spatial links created: {len(links):,}")
    print(
        "LROC products skipped due to invalid "
        f"coordinates: {skipped_products:,}"
    )
    print("Relationship:")
    print("  center_inside_feature_bounds")
    print()
    print("Important:")
    print("  These are bounding-box spatial links only.")
    print(
        "  They do NOT assert that an LROC product "
        "observes the named feature."
    )
    print()
    print("Output:")
    print(f"  {output.relative_to(ROOT)}")

    return True


# ============================================================
# STEP 8
# DATASET SUMMARY
# ============================================================

def generate_summary():

    print_stage(
        10,
        "DATASET SUMMARY"
    )

    feature_file = (
        FEATURE_DIR /
        "lunar_features.csv"
    )

    dataset_file = (
        DATASET_DIR /
        "dataset_catalogue.csv"
    )

    lola_file = (
        DATASET_DIR /
        "lola_rdr_catalogue.csv"
    )

    lroc_file = (
        DATASET_DIR /
        "lroc_rdr_catalogue.csv"
    )

    source_file = (
        SOURCE_DIR /
        "sources.csv"
    )

    observation_file = (
        OBS_DIR /
        "lunar_observations.csv"
    )

    papers_file = (
        RESEARCH_DIR /
        "research_papers.csv"
    )

    findings_file = (
        RESEARCH_DIR /
        "research_findings.csv"
    )

    summary = [

        (
            "Lunar features",
            count_csv_records(
                feature_file
            )
        ),

        (
            "Datasets",
            count_csv_records(
                dataset_file
            )
        ),

        (
            "NASA LOLA RDR products",
            count_csv_records(
                lola_file
            )
        ),

        (
            "NASA LROC RDR products",
            count_csv_records(
                lroc_file
            )
        ),

        (
            "Sources",
            count_csv_records(
                source_file
            )
        ),

        (
            "Scientific observations",
            count_csv_records(
                observation_file
            )
        ),

        (
            "Research papers",
            count_csv_records(
                papers_file
            )
        ),

        (
            "Research findings",
            count_csv_records(
                findings_file
            )
        ),
    ]

    print()

    for name, count in summary:

        print(
            f"{name:<32}"
            f"{count:>10,}"
        )

    summary_file = (
        PROCESSED_DIR /
        "dataset_summary.csv"
    )

    summary_rows = [

        {
            "component": name,
            "record_count": count,
            "generated_on":
                date.today().isoformat(),
        }

        for name, count in summary
    ]

    write_csv(
        summary_file,
        [
            "component",
            "record_count",
            "generated_on"
        ],
        summary_rows
    )

    print()
    print("Summary saved to:")

    print(
        f"  {summary_file.relative_to(ROOT)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "        DIGITAL MOON TWIN - DATASET PIPELINE"
    )
    print("=" * 70)

    print()
    print(
        f"Project root: {ROOT}"
    )

    validate_project()

    if not process_features():

        print(
            "\nFeature processing failed."
        )

        print(
            "Pipeline stopped."
        )

        sys.exit(1)

    build_dataset_catalogue()

    build_lola_catalogue()

    build_lroc_catalogue()

    build_sources()

    build_observations()

    build_research()

    build_lroc_feature_links()

    generate_summary()

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print()
    print("Your important outputs are:")

    outputs = [

        FEATURE_DIR /
        "lunar_features.csv",

        DATASET_DIR /
        "dataset_catalogue.csv",

        DATASET_DIR /
        "lola_rdr_catalogue.csv",

        DATASET_DIR /
        "lroc_rdr_catalogue.csv",

        SOURCE_DIR /
        "sources.csv",

        OBS_DIR /
        "lunar_observations.csv",

        RESEARCH_DIR /
        "research_papers.csv",

        RESEARCH_DIR /
        "research_findings.csv",

        PROCESSED_DIR /
        "lroc_feature_spatial_links.csv",

        PROCESSED_DIR /
        "dataset_summary.csv",
    ]

    for output in outputs:

        if output.exists():

            print(
                f"  [OK] "
                f"{output.relative_to(ROOT)}"
            )

        else:

            print(
                f"  [--] "
                f"{output.relative_to(ROOT)}"
            )

    print()
    print(
        "Next phase:"
    )

    print(
        "Populate verified scientific observations "
        "and research findings."
    )

    print(
        "Do NOT manually invent measurement values."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
