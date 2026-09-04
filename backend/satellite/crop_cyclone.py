from importlib import import_module


try:
    Scene = import_module("satpy").Scene
except ImportError as exc:
    raise ImportError(
        "The 'satpy' package is required. Install it with: pip install satpy"
    ) from exc
try:
    create_area_def = import_module("pyresample").create_area_def
except ImportError as exc:
    raise ImportError(
        "The 'pyresample' package is required. Install it with: pip install pyresample"
    ) from exc
from glob import glob
import os


# ==========================================
# CONFIGURATION
# ==========================================

INPUT_FOLDER = "data/raw/satellite/nisarga_20200603_1200"

OUTPUT_FOLDER = "data/processed/satellite/nisarga_20200603_1200"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# NISARGA position from IBTrACS
LAT = 19.1
LON = 73.7


# Geographic area around cyclone
LON_MIN = 69.9
LON_MAX = 75.9
LAT_MIN = 15.1
LAT_MAX = 21.1


# ==========================================
# FIND B13 FILES
# ==========================================

files = sorted(
    glob(
        os.path.join(
            INPUT_FOLDER,
            "*B13*.DAT.bz2"
        )
    )
)


print("\n==========================================")
print("   CYCLONEAI REPROJECT + CROP PROCESSOR")
print("==========================================\n")

print("B13 files found:", len(files))


# ==========================================
# LOAD HIMAWARI
# ==========================================

print("\nLoading Himawari-8 B13...")

scene = Scene(
    filenames=files,
    reader="ahi_hsd"
)

scene.load(["B13"])

print("B13 loaded successfully.")


# ==========================================
# CREATE LAT/LON GRID
# ==========================================

print("\nCreating geographic grid...")

area_def = create_area_def(
    "nisarga_region",
    {
        "proj": "latlong",
        "datum": "WGS84"
    },
    area_extent=(
        LON_MIN,
        LAT_MIN,
        LON_MAX,
        LAT_MAX
    ),
    shape=(512, 512)
)

print("Geographic grid created.")
print("Output size: 512 x 512")


# ==========================================
# REPROJECT
# ==========================================

print("\nReprojecting Himawari data...")

reprojected = scene.resample(
    area_def,
    resampler="nearest"
)

print("Reprojection completed successfully.")


# ==========================================
# SAVE REPROJECTED IMAGE
# ==========================================

output_file = os.path.join(
    OUTPUT_FOLDER,
    "nisarga_b13_geographic_512.png"
)

print("\nSaving geographic image...")

reprojected.save_dataset(
    "B13",
    filename=output_file
)


# ==========================================
# DONE
# ==========================================

print("\n==========================================")
print("       PROCESSING COMPLETED")
print("==========================================")

print("\nCyclone center:")
print(f"Latitude  : {LAT}")
print(f"Longitude : {LON}")

print("\nGeographic extent:")
print(f"Longitude : {LON_MIN} to {LON_MAX}")
print(f"Latitude  : {LAT_MIN} to {LAT_MAX}")

print("\nOutput:")
print(output_file)