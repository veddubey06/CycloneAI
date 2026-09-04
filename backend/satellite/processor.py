from pathlib import Path
from satpy import Scene


# ==========================================
# CONFIGURATION
# ==========================================

RAW_BASE = Path("data/raw/satellite")
OUTPUT_BASE = Path("data/processed/satellite")


# ==========================================
# PROCESS ONE SATELLITE TIMESTAMP
# ==========================================

def process_timestamp(folder):

    b13_files = sorted(folder.glob("*B13*.DAT.bz2"))

    if not b13_files:
        print(f"SKIP: {folder.name} - no B13 files")
        return False

    print("\n==========================================")
    print(f"PROCESSING: {folder.name}")
    print("==========================================")

    print(f"B13 files found: {len(b13_files)}")

    try:

        # --------------------------------------
        # Load Himawari-8
        # --------------------------------------

        scene = Scene(
            filenames=[str(f) for f in b13_files],
            reader="ahi_hsd"
        )

        print("Himawari files loaded successfully.")

        # --------------------------------------
        # Load Band 13
        # --------------------------------------

        print("Loading B13 infrared band...")

        scene.load(["B13"])

        print("B13 loaded successfully.")

        # --------------------------------------
        # Output directory
        # --------------------------------------

        output_folder = OUTPUT_BASE / folder.name
        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # --------------------------------------
        # Full-disk image
        # --------------------------------------

        output_file = (
            output_folder /
            f"{folder.name}_b13_full_disk.png"
        )

        print("Saving satellite image...")

        scene.save_dataset(
            "B13",
            filename=str(output_file)
        )

        print("\nPROCESSING COMPLETED")
        print("------------------------------------------")
        print(f"Output: {output_file}")

        return True

    except Exception as e:

        print("\nPROCESSING FAILED")
        print("------------------------------------------")
        print(f"Folder: {folder.name}")
        print(f"Error : {e}")

        return False


# ==========================================
# MAIN
# ==========================================

def main():

    print("\n==========================================")
    print("       CYCLONEAI SATELLITE PROCESSOR")
    print("==========================================")

    RAW_BASE.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_BASE.mkdir(
        parents=True,
        exist_ok=True
    )

    folders = sorted(
        [
            folder
            for folder in RAW_BASE.iterdir()
            if folder.is_dir()
        ]
    )

    print(f"\nSatellite timestamps found: {len(folders)}")

    if not folders:

        print("\nNo satellite folders found.")
        return

    processed = 0

    for folder in folders:

        if process_timestamp(folder):
            processed += 1

    print("\n==========================================")
    print("       PROCESSING SUMMARY")
    print("==========================================")

    print(f"Folders found     : {len(folders)}")
    print(f"Successfully done : {processed}")

    print("\nProcessing finished.")


# ==========================================

if __name__ == "__main__":
    main()