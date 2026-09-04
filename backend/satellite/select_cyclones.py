import json
from pathlib import Path

from database.database import SessionLocal
from database.models import Cyclone


# ==========================================
# CONFIGURATION
# ==========================================

MIN_YEAR = 2015
MAX_YEAR = 2025

MAX_STORMS = 12

OUTPUT_FILE = Path("data/processed/selected_cyclones.json")


# ==========================================
# SELECT CYCLONES
# ==========================================

def main():

    print("\n==========================================")
    print("       CYCLONEAI STORM SELECTOR")
    print("==========================================\n")

    db = SessionLocal()

    # --------------------------------------
    # Get valid named storms
    # --------------------------------------

    storms = (
        db.query(Cyclone)
        .filter(Cyclone.year >= MIN_YEAR)
        .filter(Cyclone.year <= MAX_YEAR)
        .filter(Cyclone.name.isnot(None))
        .filter(Cyclone.max_wind.isnot(None))
        .filter(Cyclone.max_wind > 0)
        .order_by(Cyclone.max_wind.desc())
        .all()
    )

    # Remove unnamed storms
    storms = [
        storm for storm in storms
        if storm.name.strip().upper() != "UNNAMED"
        and storm.storm_id
    ]

    print(f"Valid named storms found : {len(storms)}")

    # --------------------------------------
    # Select strongest named storm from
    # each year
    # --------------------------------------

    selected = []
    used_years = set()

    for storm in storms:

        if storm.year in used_years:
            continue

        selected.append(storm)
        used_years.add(storm.year)

        if len(selected) >= MAX_STORMS:
            break

    # --------------------------------------
    # Add NISARGA if available
    # --------------------------------------

    nisarga = (
        db.query(Cyclone)
        .filter(Cyclone.name == "NISARGA")
        .first()
    )

    if nisarga and nisarga not in selected:

        if len(selected) >= MAX_STORMS:
            selected[-1] = nisarga
        else:
            selected.append(nisarga)

    # --------------------------------------
    # Sort chronologically
    # --------------------------------------

    selected.sort(
        key=lambda storm: (
            storm.year,
            -(storm.max_wind or 0)
        )
    )

    # --------------------------------------
    # Display
    # --------------------------------------

    print(f"Selected storms          : {len(selected)}\n")

    print("==========================================")
    print("          SELECTED CYCLONES")
    print("==========================================\n")

    for number, storm in enumerate(selected, start=1):

        print(
            f"{number:02d}. "
            f"{storm.name:<15} "
            f"{storm.year} | "
            f"{storm.basin:<8} | "
            f"Wind: {storm.max_wind:>5.1f} kt | "
            f"ID: {storm.storm_id}"
        )

    # --------------------------------------
    # Dataset diversity summary
    # --------------------------------------

    print("\n==========================================")
    print("          DATASET DIVERSITY")
    print("==========================================\n")

    years = sorted(
        set(storm.year for storm in selected)
    )

    basins = sorted(
        set(storm.basin for storm in selected)
    )

    print("Years selected:")
    print(years)

    print("\nBasins selected:")

    for basin in basins:

        count = sum(
            1 for storm in selected
            if storm.basin == basin
        )

        print(f"  {basin}: {count}")

    # ======================================
    # SAVE SELECTED CYCLONES
    # ======================================

    dataset = []

    for storm in selected:

        dataset.append({
            "id": storm.id,
            "storm_id": storm.storm_id,
            "name": storm.name,
            "year": storm.year,
            "basin": storm.basin,
            "latitude": storm.latitude,
            "longitude": storm.longitude,
            "max_wind": storm.max_wind,
            "min_pressure": storm.min_pressure,
            "category": storm.category,
            "movement": storm.movement
        })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            indent=4
        )

    print("\n==========================================")
    print("       SELECTION SAVED SUCCESSFULLY")
    print("==========================================\n")

    print(f"File: {OUTPUT_FILE}")
    print(f"Storms saved: {len(dataset)}")

    db.close()


if __name__ == "__main__":
    main()