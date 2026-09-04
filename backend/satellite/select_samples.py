from database.database import SessionLocal
from database.models import Cyclone, CycloneTrack


# ==========================================
# CONFIGURATION
# ==========================================

STORM_NAME = "NISARGA"


# ==========================================
# DATABASE
# ==========================================

db = SessionLocal()


print("\n==========================================")
print("       CYCLONEAI SAMPLE SELECTOR")
print("==========================================\n")


# ==========================================
# FIND CYCLONE
# ==========================================

cyclone = (
    db.query(Cyclone)
    .filter(Cyclone.name == STORM_NAME)
    .first()
)


if not cyclone:

    print("Cyclone not found:", STORM_NAME)

    db.close()

    raise SystemExit


print("Cyclone found:")
print("ID       :", cyclone.id)
print("Storm ID :", cyclone.storm_id)
print("Name     :", cyclone.name)
print("Year     :", cyclone.year)
print("Basin    :", cyclone.basin)


# ==========================================
# GET TRACK
# ==========================================

tracks = (
    db.query(CycloneTrack)
    .filter(
        CycloneTrack.cyclone_id == cyclone.id
    )
    .order_by(
        CycloneTrack.timestamp
    )
    .all()
)


print("\nTotal track points:", len(tracks))


# ==========================================
# DISPLAY USEFUL POINTS
# ==========================================

print("\n==========================================")
print("       AVAILABLE TRAINING POINTS")
print("==========================================\n")


for track in tracks:

    if (
        track.wind_speed is None
        or track.latitude is None
        or track.longitude is None
    ):
        continue

    print(
        f"{track.timestamp} | "
        f"Lat: {track.latitude:5.1f} | "
        f"Lon: {track.longitude:5.1f} | "
        f"Wind: {track.wind_speed:5.1f} kt | "
        f"Pressure: {track.pressure}"
    )


# ==========================================
# CLOSE DATABASE
# ==========================================

db.close()


print("\n==========================================")
print("              SELECTION DONE")
print("==========================================")