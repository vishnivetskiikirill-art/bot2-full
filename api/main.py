# api/main.py
import json
from pathlib import Path
from fastapi import FastAPI, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import Base, Listing

app = FastAPI(title="Bot2 API")

DATA_PATH = Path(__file__).parent / "data" / "listings.json"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_if_empty(db: Session):
    Base.metadata.create_all(bind=engine)

    count = db.scalar(select(func.count(Listing.id)))
    if count and count > 0:
        return

    if not DATA_PATH.exists():
        return

    items = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for it in items:
        db.add(
            Listing(
                city=it.get("city", ""),
                district=it.get("district", ""),
                type=it.get("type", ""),
                price=float(it.get("price", 0)),

                area_m2=it.get("area_m2"),
                rooms=it.get("rooms"),
                lat=it.get("lat"),
                lon=it.get("lon"),

                title_i18n=it.get("title_i18n", {}),
                desc_i18n=it.get("desc_i18n", {}),
            )
        )
    db.commit()


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filters(db: Session = next(get_db()), lang: str = Query("en")):
    # Фильтры пока НЕ переводим, просто отдаём значения как есть
    rows = db.scalars(select(Listing)).all()
    cities = sorted({r.city for r in rows if r.city})
    districts = sorted({r.district for r in rows if r.district})
    types = sorted({r.type for r in rows if r.type})
    return {"cities": cities, "districts": districts, "types": types, "lang": lang}


@app.get("/api/listings")
def listings(
    db: Session = next(get_db()),
    lang: str = Query("en"),
    city: str | None = None,
    district: str | None = None,
    type: str | None = None,
    max_price: float | None = None,
):
    q = select(Listing)

    if city:
        q = q.where(Listing.city == city)
    if district:
        q = q.where(Listing.district == district)
    if type:
        q = q.where(Listing.type == type)
    if max_price is not None:
        q = q.where(Listing.price <= max_price)

    rows = db.scalars(q).all()

    # ВАЖНО: title/description отдаем уже локализованными
    return [
        {
            "id": r.id,
            "city": r.city,
            "district": r.district,
            "type": r.type,
            "price": r.price,

            "area_m2": r.area_m2,
            "rooms": r.rooms,
            "lat": r.lat,
            "lon": r.lon,

            "title": r.title(lang),
            "description": r.description(lang),
        }
        for r in rows
    ]
