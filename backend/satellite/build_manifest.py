import json
import subprocess
from pathlib import Path

from database.database import SessionLocal
from database.models import Cyclone, CycloneTrack


# ==========================================
# CONFIGURATION
# ==========================================

SELECTED_FILE = Path(
    "data/processed/selected_cyclones.json"
)

OUTPUT_FILE = Path(
    "data/processed/satellite_manifest.csv"
)

SAMPLES_PER_STORM = 10

AWS_BASE = (
    "s3://noaa-himawari8/AHI-L1b-FLDK"
)


# ==========================================
# LOAD SELECTED CYCLONES
# ==========================================

def load_selected_cyclones():

    with open(
        SELECTED_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# BUILD AWS PATH
# ==========================================

def build_aws_path(timestamp):

    date_part, time_part = timestamp.split(" ")

    year, month, day = date_part.split("-")
    hour, minute, _ = time_part.split(":")

    return (
        f"{AWS_BASE}/"
        f"{year}/{month}/{day}/"
        f"{hour}{minute}/"
    )


# ==========================================
# CHECK B13 AVAILABILITY
# ==========================================

def check_b13(timestamp):

    aws_path = build_aws_path(timestamp)

    result = subprocess.run(
        [
            "aws",
            "s3",
            "ls",
            "--no-sign-request",
            aws_path
        ],
        capture_output=True,
        text=True
    )

    b13_files = [
        line
        for line in result.stdout.splitlines()
        if "B13" in line
    ]

    return aws_path, len(b13_files)


# ==========================================
# MAIN
# ==========================================

def main():

    print("\n==========================================")
    print("       CYCLONEAI MULTI-STORM MANIFEST")
    print("==========================================\n")

    selected = load_selected_cyclones()

    print(
        f"Selected cyclones : {len(selected)}"
    )

    db = SessionLocal()

    manifest = []

    total_selected = 0

    # ======================================
    # PROCESS EACH CYCLONE
    # ======================================

    for storm_number, storm_data in enumerate(
        selected,
        start=1
    ):

        storm_id = storm_data["storm_id"]

        cyclone = (
            db.query(Cyclone)
            .filter(
                Cyclone.storm_id == storm_id
            )
            .first()
        )

        if not cyclone:

            print(
                f"\nWARNING: {storm_id} not found."
            )

            continue

        tracks = (
            db.query(CycloneTrack)
            .filter(
                CycloneTrack.cyclone_id
                == cyclone.id
            )
            .order_by(
                CycloneTrack.timestamp
            )
            .all()
        )

        print("\n------------------------------------------")
        print(
            f"{storm_number:02d}. "
            f"{cyclone.name} "
            f"({cyclone.year})"
        )
        print(
            f"    Storm ID : {cyclone.storm_id}"
        )
        print(
            f"    Tracks   : {len(tracks)}"
        )
        print("------------------------------------------")

        storm_samples = 0

        for track in tracks:

            if storm_samples >= SAMPLES_PER_STORM:
                break

            timestamp = track.timestamp

            # ----------------------------------
            # Validate scientific data
            # ----------------------------------

            values = [
                track.latitude,
                track.longitude,
                track.wind_speed,
                track.pressure
            ]

            invalid = any(
                value is None
                or not isinstance(
                    value,
                    (int, float)
                )
                for value in values
            )

            if invalid:

                print(
                    f"SKIP {timestamp} "
                    f"| invalid track data"
                )

                continue

            if track.wind_speed <= 0:

                print(
                    f"SKIP {timestamp} "
                    f"| invalid wind"
                )

                continue

            if track.pressure <= 0:

                print(
                    f"SKIP {timestamp} "
                    f"| invalid pressure"
                )

                continue

            # ----------------------------------
            # Check Himawari
            # ----------------------------------

            print(
                f"CHECK {timestamp}"
            )

            print(
                f"    Location : "
                f"{track.latitude}, "
                f"{track.longitude}"
            )

            print(
                f"    Wind     : "
                f"{track.wind_speed} kt"
            )

            print(
                f"    Pressure : "
                f"{track.pressure} hPa"
            )

            aws_path, b13_count = check_b13(
                timestamp
            )

            if b13_count == 0:

                print(
                    "    B13      : NOT AVAILABLE"
                )

                continue

            print(
                f"    B13      : "
                f"{b13_count} files AVAILABLE"
            )

            manifest.append({

                "storm_id":
                    cyclone.storm_id,

                "name":
                    cyclone.name,

                "year":
                    cyclone.year,

                "basin":
                    cyclone.basin,

                "timestamp":
                    timestamp,

                "latitude":
                    track.latitude,

                "longitude":
                    track.longitude,

                "wind_speed":
                    track.wind_speed,

                "pressure":
                    track.pressure,

                "aws_path":
                    aws_path,

                "b13_files":
                    b13_count
            })

            storm_samples += 1
            total_selected += 1

            print(
                f"    SELECTED "
                f"#{storm_samples}"
            )

        print(
            f"\nSamples selected for "
            f"{cyclone.name}: "
            f"{storm_samples}"
        )

    db.close()

    # ======================================
    # SAVE CSV
    # ======================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    import csv

    fieldnames = [
        "storm_id",
        "name",
        "year",
        "basin",
        "timestamp",
        "latitude",
        "longitude",
        "wind_speed",
        "pressure",
        "aws_path",
        "b13_files"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(manifest)

    # ======================================
    # SUMMARY
    # ======================================

    print("\n==========================================")
    print("       MANIFEST CREATED SUCCESSFULLY")
    print("==========================================\n")

    print(
        f"Cyclones processed : "
        f"{len(selected)}"
    )

    print(
        f"Samples selected   : "
        f"{total_selected}"
    )

    print(
        f"Output             : "
        f"{OUTPUT_FILE}"
    )

    print("\n==========================================\n")


if __name__ == "__main__":
    main()