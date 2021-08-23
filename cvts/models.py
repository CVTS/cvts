"""Module providing an ORM for objects of interest."""

from sqlalchemy import (
    Column,
    BigInteger,
    SmallInteger,
    Integer,
    String,
    Float,
    ForeignKey)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

DBase = declarative_base()

class Vehicle(DBase):
    """Data on a vehicle."""
    __tablename__ = 'vehicles'
    id            = Column(Integer, primary_key=True)
    vehicle_type_id = Column(Integer, ForeignKey('vehicle_types.id'))
    vehicle_type  = relationship("VehicleType")
    rego          = Column(String, unique=True)

class VehicleType(DBase):
    """A list of vehicle types."""
    __tablename__ = 'vehicle_types'
    id            = Column(Integer, primary_key=True)
    type_en       = Column(String, unique=True)
    type_vn       = Column(String, unique=True)

class Base(DBase):
    """The location a vehicle is garraged."""
    __tablename__ = 'bases'
    id            = Column(Integer, primary_key=True)
    vehicle_id    = Column(Integer, ForeignKey('vehicles.id'))
    vehicle       = relationship('Vehicle', backref=backref('base', uselist=False))
    lon           = Column(Float)
    lat           = Column(Float)

class Stop(DBase):
    """The location a vehicle is garraged."""
    __tablename__ = 'stops'
    id            = Column(Integer, primary_key=True)
    vehicle_id    = Column(Integer, ForeignKey('vehicles.id'))
    vehicle       = relationship('Vehicle', backref='stops')
    n_stationary  = Column(Integer)
    start_time    = Column(Integer)
    end_time      = Column(Integer)
    start_end_dist= Column(Float)
    start_lat     = Column(Float)
    start_lon     = Column(Float)
    end_lat       = Column(Float)
    end_lon       = Column(Float)

class Trip(DBase):
    """The location a vehicle is garraged."""
    __tablename__ = 'trips'
    id            = Column(Integer, primary_key=True)
    vehicle_id    = Column(Integer, ForeignKey('vehicles.id'))
    vehicle       = relationship('Vehicle', backref='trips')
    start_id      = Column(Integer, ForeignKey('stops.id'))
    start         = relationship('Stop',
            foreign_keys=[start_id],
            backref=backref('start', uselist=False))
    end_id        = Column(Integer, ForeignKey('stops.id'))
    end           = relationship('Stop',
            foreign_keys=[end_id],
            backref=backref('end', uselist=False))

class Traversal(DBase):
    """A traversal of a :py:class:`Segment`."""
    __tablename__ = 'traversals'
    id            = Column(Integer, primary_key=True)
    vehicle_id    = Column(Integer, ForeignKey('vehicles.id'))
    vehicle       = relationship('Vehicle', backref='traversals')
    trip_id       = Column(Integer, ForeignKey('trips.id'))
    trip          = relationship('Trip', backref='traversals')
    edge          = Column(BigInteger) # will be unsigned 64 bit int
    timestamp     = Column(Integer)
    speed         = Column(Float)
    count         = Column(Float)
