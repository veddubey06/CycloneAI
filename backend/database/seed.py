from database.database import SessionLocal, engine, Base
from database.models import Cyclone, CycloneTrack


# Create database tables
Base.metadata.create_all(bind=engine)


db = SessionLocal()


# Check whether cyclone already exists
cyclone = db.query(Cyclone).first()


if not cyclone:

    cyclone = Cyclone(
        name="Demo Cyclone",
        year=2026,
        basin="North Indian Ocean",
        latitude=18.2,
        longitude=88.4,
        max_wind=142,
        min_pressure=948,
        category="Very Severe Cyclonic Storm",
        movement="NW"
    )

    db.add(cyclone)
    db.commit()
    db.refresh(cyclone)

    print("Cyclone inserted successfully.")

else:

    print("Cyclone already exists.")


# Check whether track data exists
existing_track = (
    db.query(CycloneTrack)
    .filter(CycloneTrack.cyclone_id == cyclone.id)
    .first()
)


if not existing_track:

    track_points = [

        CycloneTrack(
            cyclone_id=cyclone.id,
            timestamp="2026-09-01 00:00",
            latitude=15.2,
            longitude=91.5,
            wind_speed=55,
            pressure=998
        ),

        CycloneTrack(
            cyclone_id=cyclone.id,
            timestamp="2026-09-01 06:00",
            latitude=15.8,
            longitude=90.7,
            wind_speed=65,
            pressure=992
        ),

        CycloneTrack(
            cyclone_id=cyclone.id,
            timestamp="2026-09-01 12:00",
            latitude=16.5,
            longitude=89.9,
            wind_speed=80,
            pressure=985
        ),

        CycloneTrack(
            cyclone_id=cyclone.id,
            timestamp="2026-09-01 18:00",
            latitude=17.2,
            longitude=89.1,
            wind_speed=100,
            pressure=975
        ),

        CycloneTrack(
            cyclone_id=cyclone.id,
            timestamp="2026-09-02 00:00",
            latitude=18.2,
            longitude=88.4,
            wind_speed=142,
            pressure=948
        )
    ]

    db.add_all(track_points)
    db.commit()

    print("Cyclone track inserted successfully.")

else:

    print("Track data already exists.")


db.close()