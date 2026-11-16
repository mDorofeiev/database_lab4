import enum
from sqlalchemy import (
    Column, Integer, String, Float, Date, Time, Boolean, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from src.database import Base

class WindDirection(str, enum.Enum):
    N = 'N'
    NNE = 'NNE'
    NE = 'NE'
    ENE = 'ENE'
    E = 'E'
    ESE = 'ESE'
    SE = 'SE'
    SSE = 'SSE'
    S = 'S'
    SSW = 'SSW'
    SW = 'SW'
    WSW = 'WSW'
    W = 'W'
    WNW = 'WNW'
    NW = 'NW'
    NNW = 'NNW'

class WeatherReport(Base):
    __tablename__ = 'weather_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=False, index=True)
    location_name = Column(String(100), nullable=False, index=True)
    temperature_celsius = Column(Float, nullable=False)
    last_updated = Column(Date, nullable=False, index=True)
    sunrise = Column(Time, nullable=False)

    wind_info = relationship(
        'WindInfo',
        back_populates='weather_report',
        uselist=False,
        cascade='all, delete-orphan'
    )

class WindInfo(Base):
    __tablename__ = 'wind_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    weather_report_id = Column(Integer, ForeignKey('weather_reports.id', ondelete='CASCADE'), nullable=False, unique=True)
    wind_mph = Column(Float, nullable=False)
    wind_kph = Column(Float, nullable=False)
    wind_degree = Column(Integer, nullable=False)
    wind_direction = Column(Enum(WindDirection, name='wind_direction_enum'), nullable=False)
    gust_mph = Column(Float, nullable=False)
    gust_kph = Column(Float, nullable=False)
    should_go_outside = Column(Boolean, nullable=False, default=True)
    weather_report = relationship('WeatherReport', back_populates='wind_info')