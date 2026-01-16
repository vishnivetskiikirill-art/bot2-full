from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # core
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    area_m2: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    rooms: Mapped[int] = mapped_column(Integer, nullable=False)

    # geo (optional)
    lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)

    # text
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    images: Mapped[List["PropertyImage"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    property: Mapped["Property"] = relationship(back_populates="images")
