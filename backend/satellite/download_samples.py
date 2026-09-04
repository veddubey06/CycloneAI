from pathlib import Path
import subprocess
import math

from database.database import SessionLocal
from database.models import Cyclone, CycloneTrack


# ==========================================
# CONFIGURATION
# ==========================================

STORM_ID = "2020153N13072"

MAX_NEW_SAMPLES = 3

RAW_BASE = Path("data/raw/satellite")

AWS_BASE = "s3://noaa-himawari8/AHI-L1b-FLDK"


# ==========================================
# VALIDATION
# ==========================================

def valid_track(track):

    values = [
        track.latitude,
        track.longitude,
        track.wind_speed,
        track.pressure
    ]

    return not any(
        value is None
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        for value in values
    )


# ==========================================
# TIMESTAMP → AWS PATH
# ==========================================

def get_aws_path(timestamp):

    date_part, time_part = timestamp.split(" ")

    year, month, day = date_part.split("-")
    hour, minute, _ = time_part.split(":")

    return (
        f"{AWS_BASE}/"
        f"{year}/{month}/{day}/"
        f"{hour}{minute}/"
    )


# ==========================================
# DOWNLOAD B13
# ==========================================

def download_b13(timestamp, output_folder):

    aws_path = get_aws_path(timestamp)

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "aws",
        "s3",
        "cp",
        "--no-sign-request",
        aws_path,
        str(output_folder),
        "--recursive",
        "--exclude",
        "*",
        "--include",
        "*B13*"
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        return False

    files = list(output_folder.glob("*B13*.bz2"))

    return len(files) > 0


# ==========================================
# MAIN
# ==========================================

def main():

    print("\n==========================================")
    print("       CYCLONEAI B13 DOWNLOADER")
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
        .filter(
            CycloneTrack.cyclone_id == cyclone.id
        )
        .order_by(CycloneTrack.timestamp)
        .all()
    )

    print("Track points:", len(tracks))

    downloaded = 0

    print("\n==========================================")
    print("        DOWNLOADING B13 SAMPLES")
    print("==========================================\n")

    for track in tracks:

        if downloaded >= MAX_NEW_SAMPLES:
            break

        # ----------------------------------
        # Validate scientific data
        # ----------------------------------

        if not valid_track(track):

            print(
                f"SKIP {track.timestamp} "
                f"→ invalid track data"
            )

            continue

        # ----------------------------------
        # Folder name
        # ----------------------------------

        timestamp = track.timestamp

        clean_timestamp = (
            timestamp
            .replace("-", "")
            .replace(":", "")
            .replace(" ", "_")
        )

        folder_name = (
            f"{cyclone.name.lower()}_{clean_timestamp[:15]}"
        )

        output_folder = RAW_BASE / folder_name

        # ----------------------------------
        # Already downloaded?
        # ----------------------------------

        existing_files = list(
            output_folder.glob("*B13*.bz2")
        ) if output_folder.exists() else []

        if len(existing_files) >= 10:

            print(
                f"SKIP {timestamp} "
                f"→ already downloaded ({len(existing_files)} files)"
            )

            continue

        # ----------------------------------
        # Download
        # ----------------------------------

        print("------------------------------------------")
        print(f"Downloading: {timestamp}")
        print(
            f"Location: "
            f"{track.latitude}, {track.longitude}"
        )
        print(f"Wind: {track.wind_speed} kt")
        print(f"Pressure: {track.pressure} hPa")

        print("\nAWS:")
        print(get_aws_path(timestamp))

        success = download_b13(
            timestamp,
            output_folder
        )

        files = list(
            output_folder.glob("*B13*.bz2")
        )

        if success:

            print(
                f"\nDownloaded B13 files: "
                f"{len(files)} ✅"
            )

            downloaded += 1

        else:

            print("\nDownload failed ❌")

    db.close()

    print("\n==========================================")
    print("        DOWNLOAD COMPLETED")
    print("==========================================")

    print(
        f"\nNew samples downloaded: {downloaded}"
    )


if __name__ == "__main__":
    main()