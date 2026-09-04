from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import Cyclone, CycloneTrack


router = APIRouter(
    prefix="/api/cyclone",
    tags=["Cyclone"]
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# CURRENT CYCLONE
# ============================================================

@router.get("/current")
def current_cyclone():

    return {
        "name": "Demo Cyclone",
        "status": "active",
        "latitude": 18.2,
        "longitude": 88.4,
        "wind_speed": 142,
        "pressure": 948,
        "movement": "NW",
        "movement_speed": 14
    }


# ============================================================
# HISTORICAL CYCLONES
# ============================================================

@router.get("/historical")
def historical_cyclones(
    year: int | None = None,
    subbasin: str | None = None,
    category: str | None = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Cyclone)

    # Filter by year
    if year is not None:
        query = query.filter(Cyclone.year == year)

    # Filter by subbasin
    if subbasin is not None:
        query = query.filter(Cyclone.basin.contains(subbasin))

    # Filter by category
    if category is not None:
        query = query.filter(Cyclone.category == category)

    # Pagination
    cyclones = (
        query
        .order_by(Cyclone.year.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return cyclones

    # Start query
    query = db.query(Cyclone)

    # --------------------------------------------------------
    # YEAR FILTER
    # --------------------------------------------------------

    if year is not None:

        query = query.filter(
            Cyclone.year == year
        )

    # --------------------------------------------------------
    # SUBBASIN FILTER
    # --------------------------------------------------------

    if subbasin is not None:

        subbasin = subbasin.upper()

        query = query.filter(
            Cyclone.basin.like(f"%{subbasin}%")
        )

    # --------------------------------------------------------
    # NAME SEARCH
    # --------------------------------------------------------

    if name is not None:

        query = query.filter(
            Cyclone.name.ilike(
                f"%{name}%"
            )
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    query = query.order_by(
        Cyclone.year.desc(),
        Cyclone.id.desc()
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    cyclones = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return cyclones


# ============================================================
# CYCLONE TRACK
# ============================================================

@router.get("/{cyclone_id}/track")
def cyclone_track(
    cyclone_id: int,
    db: Session = Depends(get_db)
):

    track = (
        db.query(CycloneTrack)
        .filter(
            CycloneTrack.cyclone_id == cyclone_id
        )
        .order_by(
            CycloneTrack.timestamp
        )
        .all()
    )

    return track

@router.get("/stats")
def cyclone_statistics(db: Session = Depends(get_db)):

    total_cyclones = db.query(Cyclone).count()

    bay_of_bengal = (
        db.query(Cyclone)
        .filter(Cyclone.basin.contains("BB"))
        .count()
    )

    arabian_sea = (
        db.query(Cyclone)
        .filter(Cyclone.basin.contains("AS"))
        .count()
    )

    categories = {}

    cyclone_records = db.query(Cyclone).all()

    for cyclone in cyclone_records:
        category = cyclone.category or "Unknown"

        if category not in categories:
            categories[category] = 0

        categories[category] += 1

    return {
        "total_cyclones": total_cyclones,
        "bay_of_bengal": bay_of_bengal,
        "arabian_sea": arabian_sea,
        "categories": categories
    }