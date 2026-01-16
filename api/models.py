# api/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    city: Mapped[str] = mapped_column(String(120), index=True)
    district: Mapped[str] = mapped_column(String(180), index=True)
    type: Mapped[str] = mapped_column(String(80), index=True)

    price: Mapped[float] = mapped_column(Float)

    # optional fields for "details" later
    area_m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # i18n fields: {"en": "...", "ru": "...", "he": "...", "bg": "..."}
    title_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)
    desc_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)

    def pick_lang(self, d: dict, lang: str) -> str:
        if not isinstance(d, dict):
            return ""
        lang = (lang or "en").lower()
        return (
            d.get(lang)
            or d.get(lang.split("-")[0])  # на случай "ru-RU"
            or d.get("en")
            or next(iter(d.values()), "")
        )

    def title(self, lang: str) -> str:
        return self.pick_lang(self.title_i18n, lang)

    def description(self, lang: str) -> str:
        return self.pick_lang(self.desc_i18n, lang)
