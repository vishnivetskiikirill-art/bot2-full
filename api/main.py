from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from .settings import settings
from .db import engine, SessionLocal
from .models import Base, Property
from .admin import setup_admin

# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp"

# ---------------- App ----------------
app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Для SQLAdmin login session
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# Раздаём статику миниаппа: /webapp/index.html, /webapp/app.js, /webapp/styles.css
if WEBAPP_DIR.exists():
    app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")

# Создаём таблицы при старте (MVP). Потом заменим на Alembic.
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Подключаем админку
setup_admin(app, engine)

# ---------------- DB dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Helpers ----------------
def normalize_str(x: Any) -> str:
    return str(x).strip() if x is not None else ""

def property_to_dict(p: Property) -> Dict[str, Any]:
    # Формат максимально похож на твой старый JSON
    images = sorted(p.images, key=lambda im: (im.sort_order or 0, im.id))
    cover = None
    for im in images:
        if im.is_cover:
            cover = im.url
            break
    return {
        "id": p.id,
        "city": p.city,
        "district": p.district,
        "type": p.type,
        "price": float(p.price),
        "area_m2": float(p.area_m2),
        "rooms": int(p.rooms),
        "lat": float(p.lat) if p.lat is not None else None,
        "lng": float(p.lng) if p.lng is not None else None,
        "description": p.description,
        "is_active": bool(p.is_active),
        "images": [im.url for im in images],
        "cover": cover,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

# ---------------- Routes ----------------
@app.get("/api/status")
def status():
    return {"status": "ok"}

# чтобы при открытии домена сразу открывался миниапп
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/webapp/")

@app.get("/webapp/", include_in_schema=False)
def webapp_index():
    index_path = WEBAPP_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h3>webapp/index.html not found</h3>", status_code=404)
    return FileResponse(index_path)

@app.get("/api/listings")
def get_listings(
    db: Session = Depends(get_db),
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None, alias="type"),
    max_price: Optional[float] = Query(default=None),
    min_price: Optional[float] = Query(default=None),
    rooms: Optional[int] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    q = select(Property).options(selectinload(Property.images)).where(Property.is_active.is_(True))

    if city:
        q = q.where(func.lower(Property.city) == normalize_str(city).lower())
    if district:
        q = q.where(func.lower(Property.district) == normalize_str(district).lower())
    if type:
        q = q.where(func.lower(Property.type) == normalize_str(type).lower())

    if min_price is not None:
        q = q.where(Property.price >= min_price)
    if max_price is not None:
        q = q.where(Property.price <= max_price)

    if rooms is not None:
        q = q.where(Property.rooms == rooms)

    q = q.order_by(Property.id.desc()).limit(limit)

    items = db.execute(q).scalars().all()
    return [property_to_dict(p) for p in items]

@app.get("/api/filters")
def get_filters(db: Session = Depends(get_db)):
    # Достаём уникальные значения из БД
    cities = db.execute(
        select(func.distinct(Property.city)).where(Property.city.is_not(None), Property.is_active.is_(True))
    ).scalars().all()

    districts = db.execute(
        select(func.distinct(Property.district)).where(Property.district.is_not(None), Property.is_active.is_(True))
    ).scalars().all()

    types = db.execute(
        select(func.distinct(Property.type)).where(Property.type.is_not(None), Property.is_active.is_(True))
    ).scalars().all()

    # нормализуем и сортируем
    cities = sorted({normalize_str(x) for x in cities if normalize_str(x)})
    districts = sorted({normalize_str(x) for x in districts if normalize_str(x)})
    types = sorted({normalize_str(x) for x in types if normalize_str(x)})

    return {
        "cities": cities,
        "districts": districts,
        "types": types,
    }
