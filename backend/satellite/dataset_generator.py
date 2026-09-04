from pathlib import Path
import subprocess
import math

from database.database import SessionLocal
from database.models import Cyclone, CycloneTrack


# ==========================================
# CONFIGURATION
# ==========================================

STORM_ID = "2020153N13072"

MAX_NEW_SAMPLES = 30

RAW_BASE = Path("data/raw/satellite")
PROCESSED_BASE = Path("data/processed/satellite")

AWS_BASE = "s3://noaa-himawari8/AHI-L1b-FLDK"


# ==========================================
# AWS CHECK
# ==========================================

def check_b13(timestamp):
    """
    Check whether B13 Himawari files exist
    for a given timestamp.
    """

    date_part, time_part = timestamp.split(" ")

    year, month, day = date_part.split("-")
    hour, minute, _ = time_part.split(":")

    path = (
        f"{AWS_BASE}/"
        f"{year}/{month}/{day}/"
        f"{hour}{minute}/"
    )

    result = subprocess.run(
        [
            "aws",
            "s3",
            "ls",
            "--no-sign-request",
            path
        ],
        capture_output=True,
        text=True
    )

    b13_files = [
        line
        for line in result.stdout.splitlines()
        if "B13" in line
    ]

    return path, len(b13_files)


# ==========================================
# MAIN
# ==========================================

def main():

    print("\n==========================================")
    print("       CYCLONEAI DATASET GENERATOR")
    print("==========================================\n")

    db = SessionLocal()

    cyclone = (
        db.query(Cyclone)
        .filter(Cyclone.storm_id == STORM_ID)
        .first()
    )

    if not cyclone:
        print("Cyclone not found.")
        db.close()
        return

    print("Storm ID :", cyclone.storm_id)
    print("Name     :", cyclone.name)
    print("Year     :", cyclone.year)
    print("Basin    :", cyclone.basin)

    tracks = (
        db.query(CycloneTrack)
        .filter(CycloneTrack.cyclone_id == cyclone.id)
        .order_by(CycloneTrack.timestamp)
        .all()
    )

    print("Track points:", len(tracks))

    print("\n==========================================")
    print("             DRY RUN")
    print("==========================================\n")

    selected = 0

    for track in tracks:

        if selected >= MAX_NEW_SAMPLES:
            break

        timestamp = track.timestamp

        # Convert timestamp to folder name
        folder_name = (
            f"{cyclone.name.lower()}_"
            f"{timestamp.replace('-', '').replace(':', '').replace(' ', '_')[:13]}"
        )

        processed_folder = PROCESSED_BASE / folder_name

        # ----------------------------------
        # Validate scientific labels
        # ----------------------------------

        values = [
            track.latitude,
            track.longitude,
            track.wind_speed,
            track.pressure
        ]

        invalid_data = any(
            value is None
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            for value in values
        )

        if invalid_data:
            print(f"SKIP  {timestamp}")
            print("      Reason: incomplete/invalid track data\n")
            continue

        # ----------------------------------
        # Require positive intensity
        # ----------------------------------

        if track.wind_speed <= 0 or track.pressure <= 0:
            print(f"SKIP  {timestamp}")
            print("      Reason: invalid wind/pressure\n")
            continue

        # ----------------------------------
        # Already processed?
        # ----------------------------------

        processed_image = (
            processed_folder / "nisarga_b13_geographic_512.png"
        )

        if processed_image.exists():

            print(f"SKIP  {timestamp}")
            print("      Reason: sample already processed\n")

            continue

        # ----------------------------------
        # Check AWS
        # ----------------------------------

        aws_path, b13_count = check_b13(timestamp)

        print(f"CHECK {timestamp}")
        print(
            f"      Location: "
            f"{track.latitude}, {track.longitude}"
        )
        print(
            f"      Wind: {track.wind_speed} kt"
        )
        print(
            f"      Pressure: {track.pressure} hPa"
        )
        print(
            f"      B13 files: {b13_count}"
        )

        if b13_count == 0:

            print("      Status: NOT AVAILABLE ❌\n")

            continue

        print("      Status: AVAILABLE ✅")
        print(f"      AWS: {aws_path}")

        selected += 1

        print(
            f"      SELECTED #{selected} ⭐\n"
        )

    db.close()

    print("==========================================")
    print("             DRY RUN COMPLETE")
    print("==========================================")

    print(
        f"\nNew samples selected: {selected}"
    )

    print(
        "\nNo files were downloaded."
    )


if __name__ == "__main__":
    main()