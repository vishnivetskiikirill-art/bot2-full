from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)

    city = Column(String(120), index=True, nullable=True)
    district = Column(String(120), index=True, nullable=True)
    type = Column(String(120), index=True, nullable=True)

    price = Column(Float, nullable=True)
    area_m2 = Column(Float, nullable=True)
    rooms = Column(Integer, nullable=True)

    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    url = Column(Text, nullable=False)

    # порядок/позиция + признак "обложки" (необязательно, но удобно)
    sort_order = Column(Integer, default=0, nullable=False)
    is_cover = Column(Boolean, default=False, nullable=False)

    property = relationship("Property", back_populates="images")
