import os
import csv


ROOT = "MOON_DATASET"


print("=" * 70)
print("SEARCHING LUNARTWIN REPOSITORY FOR LOLA DATA")
print("=" * 70)


# ============================================================
# 1. SEARCH FILENAMES
# ============================================================

print("\n\nFILES WITH 'LOLA' IN THE NAME:")
print("-" * 70)

lola_files = []

for root, dirs, files in os.walk(ROOT):

    # Ignore git/venv-like folders if encountered
    dirs[:] = [
        d for d in dirs
        if d not in [".git", ".venv", "__pycache__"]
    ]

    for file in files:

        if "lola" in file.lower():

            path = os.path.join(root, file)
            lola_files.append(path)

            print(path)


print("\nTotal LOLA-named files:", len(lola_files))


# ============================================================
# 2. SEARCH DATASET CATALOGUE
# ============================================================

catalogue_path = (
    "MOON_DATASET/03_dataset_catalogue/"
    "dataset_catalogue.csv"
)

print("\n\nDATASET CATALOGUE:")
print("-" * 70)

if not os.path.exists(catalogue_path):

    print("❌ dataset_catalogue.csv not found")

else:

    with open(
        catalogue_path,
        newline="",
        encoding="utf-8-sig"
    ) as f:

        reader = csv.DictReader(f)

        print("Columns:")
        print(reader.fieldnames)

        print("\nLOLA records:")

        count = 0

        for row in reader:

            text = " ".join(
                str(value)
                for value in row.values()
            ).lower()

            if "lola" in text:

                print("\n", row)

                count += 1

        print("\nTotal LOLA catalogue records:", count)


# ============================================================
# 3. SEARCH RAW DATA FOR SHACKLETON
# ============================================================

print("\n\nSEARCHING FILENAMES FOR SHACKLETON:")
print("-" * 70)

shackleton_files = []

for root, dirs, files in os.walk(ROOT):

    dirs[:] = [
        d for d in dirs
        if d not in [".git", ".venv", "__pycache__"]
    ]

    for file in files:

        if "shackleton" in file.lower():

            path = os.path.join(root, file)
            shackleton_files.append(path)

            print(path)


print(
    "\nTotal filenames containing Shackleton:",
    len(shackleton_files)
)


print("\n" + "=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)