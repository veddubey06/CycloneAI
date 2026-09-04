import math
import pandas as pd

from database.database import SessionLocal, engine, Base
from database.models import Cyclone, CycloneTrack


# ============================================================
# CONFIGURATION
# ============================================================

FILE = "data/raw/ibtracs.NI.list.v04r01.csv"


# ============================================================
# IMD CYCLONE CATEGORY
# Wind speed is in knots
# ============================================================

def get_category(wind):
    if pd.isna(wind):
        return "Unknown"

    wind = float(wind)

    if wind < 28:
        return "Depression"
    elif wind < 34:
        return "Deep Depression"
    elif wind < 48:
        return "Cyclonic Storm"
    elif wind < 64:
        return "Severe Cyclonic Storm"
    elif wind < 90:
        return "Very Severe Cyclonic Storm"
    elif wind < 120:
        return "Extremely Severe Cyclonic Storm"
    else:
        return "Super Cyclonic Storm"


# ============================================================
# CALCULATE MOVEMENT DIRECTION
# ============================================================

def calculate_direction(lat1, lon1, lat2, lon2):

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    if abs(dlat) < 0.1 and abs(dlon) < 0.1:
        return "Stationary"

    angle = math.degrees(math.atan2(dlon, dlat))

    if angle < 0:
        angle += 360

    directions = [
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW"
    ]

    index = int((angle + 22.5) // 45) % 8

    return directions[index]


# ============================================================
# LOAD IBTRACS
# ============================================================

print("\n============================================")
print("       CYCLONEAI IBTRACS IMPORTER")
print("============================================\n")

print("Loading IBTrACS dataset...")

df = pd.read_csv(
    FILE,
    skiprows=[1],
    usecols=[
        "SID",
        "SEASON",
        "BASIN",
        "SUBBASIN",
        "NAME",
        "ISO_TIME",
        "NATURE",
        "LAT",
        "LON",
        "WMO_WIND",
        "WMO_PRES",
        "WMO_AGENCY"
    ],
    low_memory=False
)

print("IBTrACS loaded successfully.")
print("Total track records:", len(df))


# ============================================================
# CLEAN DATA
# ============================================================

print("\nCleaning data...")

df["SEASON"] = pd.to_numeric(df["SEASON"], errors="coerce")
df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
df["WMO_WIND"] = pd.to_numeric(df["WMO_WIND"], errors="coerce")
df["WMO_PRES"] = pd.to_numeric(df["WMO_PRES"], errors="coerce")

df["ISO_TIME"] = pd.to_datetime(
    df["ISO_TIME"],
    errors="coerce"
)

# Remove records without essential information
df = df.dropna(
    subset=[
        "SID",
        "ISO_TIME",
        "LAT",
        "LON"
    ]
)

print("Valid track records:", len(df))


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

Base.metadata.create_all(bind=engine)

db = SessionLocal()


# ============================================================
# CLEAR OLD DEMO DATA
# ============================================================

print("\nRemoving old demo data...")

db.query(CycloneTrack).delete()
db.query(Cyclone).delete()

db.commit()

print("Old data removed.")


# ============================================================
# IMPORT CYCLONES
# ============================================================

storm_ids = df["SID"].dropna().unique()

print("\n============================================")
print("Importing cyclone records...")
print("Total unique storms:", len(storm_ids))
print("============================================\n")


cyclone_count = 0
track_count = 0


for index, storm_id in enumerate(storm_ids, start=1):

    storm_df = df[df["SID"] == storm_id].copy()

    if storm_df.empty:
        continue

    storm_df = storm_df.sort_values("ISO_TIME")

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    season = storm_df["SEASON"].dropna()

    year = int(season.iloc[0]) if not season.empty else 0

    name_series = storm_df["NAME"].dropna()

    if not name_series.empty:
        name = str(name_series.iloc[0]).strip()
    else:
        name = "UNNAMED"

    if not name:
        name = "UNNAMED"

    basin_series = storm_df["BASIN"].dropna()
    basin = str(basin_series.iloc[0]) if not basin_series.empty else "NI"

    subbasin_series = storm_df["SUBBASIN"].dropna()
    subbasin = (
        str(subbasin_series.iloc[0])
        if not subbasin_series.empty
        else ""
    )

    # --------------------------------------------------------
    # Maximum wind
    # --------------------------------------------------------

    valid_wind = storm_df.dropna(
        subset=["WMO_WIND"]
    )

    if not valid_wind.empty:

        max_wind = float(
            valid_wind["WMO_WIND"].max()
        )

        # Position at maximum wind
        max_wind_row = valid_wind.loc[
            valid_wind["WMO_WIND"].idxmax()
        ]

        representative_lat = float(
            max_wind_row["LAT"]
        )

        representative_lon = float(
            max_wind_row["LON"]
        )

        category = get_category(max_wind)

    else:

        max_wind = None

        representative_lat = float(
            storm_df.iloc[-1]["LAT"]
        )

        representative_lon = float(
            storm_df.iloc[-1]["LON"]
        )

        category = "Unknown"

    # --------------------------------------------------------
    # Minimum pressure
    # --------------------------------------------------------

    valid_pressure = storm_df.dropna(
        subset=["WMO_PRES"]
    )

    if not valid_pressure.empty:
        min_pressure = float(
            valid_pressure["WMO_PRES"].min()
        )
    else:
        min_pressure = None

    # --------------------------------------------------------
    # Movement direction
    # --------------------------------------------------------

    movement = "Unknown"

    movement_df = storm_df[
        ["LAT", "LON"]
    ].dropna()

    if len(movement_df) >= 2:

        first = movement_df.iloc[-2]
        last = movement_df.iloc[-1]

        movement = calculate_direction(
            float(first["LAT"]),
            float(first["LON"]),
            float(last["LAT"]),
            float(last["LON"])
        )

    # --------------------------------------------------------
    # Create cyclone
    # --------------------------------------------------------

    cyclone = Cyclone(
        storm_id=str(storm_id),
        name=name,
        year=year,
        basin=(
            f"{basin} - {subbasin}"
            if subbasin
            else basin
        ),
        latitude=representative_lat,
        longitude=representative_lon,
        max_wind=max_wind,
        min_pressure=min_pressure,
        category=category,
        movement=movement
    )

    db.add(cyclone)
    db.flush()

    cyclone_count += 1

    # --------------------------------------------------------
    # Create track records
    # --------------------------------------------------------

    tracks = []

    for _, row in storm_df.iterrows():

        timestamp = row["ISO_TIME"]

        if pd.isna(timestamp):
            continue

        wind = row["WMO_WIND"]
        pressure = row["WMO_PRES"]

        tracks.append(
            CycloneTrack(
                cyclone_id=cyclone.id,
                timestamp=timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                latitude=float(row["LAT"]),
                longitude=float(row["LON"]),
                wind_speed=(
                    float(wind)
                    if not pd.isna(wind)
                    else None
                ),
                pressure=(
                    float(pressure)
                    if not pd.isna(pressure)
                    else None
                )
            )
        )

    db.add_all(tracks)

    track_count += len(tracks)

    # Commit every 100 storms
    if index % 100 == 0:

        db.commit()

        print(
            f"Processed {index}/{len(storm_ids)} storms "
            f"| Tracks: {track_count}"
        )


# ============================================================
# FINAL COMMIT
# ============================================================

db.commit()
db.close()


# ============================================================
# RESULT
# ============================================================

print("\n============================================")
print("       IMPORT COMPLETED SUCCESSFULLY")
print("============================================")

print(f"\nCyclones imported : {cyclone_count}")
print(f"Track points      : {track_count}")

print("\nDatabase is now using REAL IBTrACS data.")
print("============================================\n")