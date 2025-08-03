from sqlalchemy import Column, DateTime, Integer, Numeric, String
from db import Base

class WeatherCurrent(Base):
    __tablename__ = 'weather_current'

    collection_time = Column(DateTime(timezone=True), primary_key=True)
    temperature = Column(Integer)
    temperature_min = Column(Integer)
    temperature_max = Column(Integer)
    humidity = Column(Integer)
    description = Column(String(200))
    feels_like = Column(Integer)
    wind_speed = Column(Numeric)
    wind_direction = Column(Integer)
