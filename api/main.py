from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


# ----------------------------
# Paths / storage
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent            # .../api
DATA_DIR = BASE_DIR / "data"
WEBAPP_DIR = BASE_DIR / "webapp"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LISTINGS_PATH = DATA_DIR / "listings.json"

# create empty listings file if not exists
if not LISTINGS_PATH.exists():
    LISTINGS_PATH.write_text("[]", encoding="utf-8")


# ----------------------------
# Env
# ----------------------------
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")  # set in Railway Variables


# ----------------------------
# App
# ----------------------------
app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Static webapp
# ----------------------------
if not WEBAPP_DIR.exists():
    # If folder missing, show clear error in logs
    print(f"[WARN] WEBAPP_DIR not found: {WEBAPP_DIR}")

# serve css/js/images from /webapp/...
app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR)), name="webapp")


@app.get("/", include_in_schema=False)
def serve_index():
    """Mini App must open HTML, not JSON."""
    index_file = WEBAPP_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail=f"index.html not found in {WEBAPP_DIR}")
    return FileResponse(index_file)


# ----------------------------
# Helpers
# ----------------------------
def _read_listings() -> List[Dict[str, Any]]:
    try:
        raw = LISTINGS_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def _write_listings(items: List[Dict[str, Any]]) -> None:
    LISTINGS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = str(s).strip()
    return s if s else None


def _as_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


# ----------------------------
# API
# ----------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filters():
    """
    Возвращает доступные значения фильтров из базы (сейчас из listings.json)
    """
    items = _read_listings()
    cities = sorted({i.get("city", "").strip() for i in items if i.get("city")})
    districts = sorted({i.get("district", "").strip() for i in items if i.get("district")})
    types_ = sorted({i.get("type", "").strip() for i in items if i.get("type")})

    return {
        "cities": cities,
        "districts": districts,
        "types": types_,
    }


@app.get("/api/listings")
def get_listings(
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    max_price: Optional[int] = Query(default=None, ge=0),
):
    """
    Получить список объявлений с фильтрами
    """
    items = _read_listings()

    city = _normalize(city)
    district = _normalize(district)
    type = _normalize(type)

    result = []
    for it in items:
        if city and _normalize(it.get("city")) != city:
            continue
        if district and _normalize(it.get("district")) != district:
            continue
        if type and _normalize(it.get("type")) != type:
            continue

        price = _as_int(it.get("price"), default=0)
        if max_price is not None and price > max_price:
            continue

        result.append(it)

    return {"count": len(result), "items": result}


@app.post("/api/admin/add")
def admin_add_listing(payload: Dict[str, Any] = Body(...)):
    """
    Добавить объявление.
    Требует ключ: ADMIN_API_KEY
    Передавать в payload:
      {
        "key": "...",
        "title": "...",
        "description": "...",
        "price": 100000,
        "city": "...",
        "district": "...",
        "type": "...",
        "contact": "t.me/username или телефон",
        "photos": ["url1", "url2"]  (необязательно)
      }
    """
    key = payload.get("key")
    if key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid ADMIN_API_KEY")

    title = _normalize(payload.get("title"))
    description = _normalize(payload.get("description"))
    contact = _normalize(payload.get("contact"))
    city = _normalize(payload.get("city"))
    district = _normalize(payload.get("district"))
    type_ = _normalize(payload.get("type"))

    price = _as_int(payload.get("price"), default=0)
    if not title or not description or not contact or not city or not type_:
        raise HTTPException(
            status_code=400,
            detail="Required: title, description, contact, city, type",
        )

    photos = payload.get("photos") or []
    if not isinstance(photos, list):
        photos = []

    items = _read_listings()
    new_id = (max([_as_int(i.get("id"), 0) for i in items]) + 1) if items else 1

    item = {
        "id": new_id,
        "title": title,
        "description": description,
        "price": price,
        "city": city,
        "district": district or "",
        "type": type_,
        "contact": contact,
        "photos": photos,
    }

    items.append(item)
    _write_listings(items)

    return {"ok": True, "item": item}


@app.post("/api/admin/delete")
def admin_delete_listing(payload: Dict[str, Any] = Body(...)):
    """
    Удалить объявление по id.
    payload: {"key":"...","id":123}
    """
    key = payload.get("key")
    if key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid ADMIN_API_KEY")

    del_id = _as_int(payload.get("id"), 0)
    if del_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id")

    items = _read_listings()
    new_items = [i for i in items if _as_int(i.get("id"), 0) != del_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="Not found")

    _write_listings(new_items)
    return {"ok": True, "deleted_id": del_id}


