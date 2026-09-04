from sqlalchemy import Column, Integer, Float, String
from database.database import Base


class Cyclone(Base):

    __tablename__ = "cyclones"

    id = Column(Integer, primary_key=True, index=True)

    storm_id = Column(String, unique=True, index=True)

    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    basin = Column(String, nullable=False)

    latitude = Column(Float)
    longitude = Column(Float)

    max_wind = Column(Float)
    min_pressure = Column(Float)

    category = Column(String)

    movement = Column(String)

class CycloneTrack(Base):

    __tablename__ = "cyclone_tracks"

    id = Column(Integer, primary_key=True, index=True)

    cyclone_id = Column(
        Integer, 
        nullable=False
    )

    timestamp = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    wind_speed = Column(Float)
    pressure = Column(Float)


