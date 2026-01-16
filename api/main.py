from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent          # .../api
WEBAPP_DIR = BASE_DIR / "webapp"                    # .../api/webapp
DATA_FILE = BASE_DIR / "data" / "listings.json"     # .../api/data/listings.json


# ---------- App ----------
app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # для мини-аппа удобно, потом можно ограничить
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Helpers ----------
def load_listings() -> List[Dict[str, Any]]:
    """
    Читает listings.json как список объектов.
    Если файла нет/битый — возвращает [].
    """
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # гарантируем что элементы словари
            return [x for x in data if isinstance(x, dict)]
        return []
    except Exception:
        return []


def norm(s: Optional[str]) -> str:
    return (s or "").strip()


def uniq_sorted(values: List[str]) -> List[str]:
    cleaned = [v.strip() for v in values if v and v.strip()]
    return sorted(list(set(cleaned)))


# ---------- Static webapp ----------
if WEBAPP_DIR.exists():
    app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")


# ---------- Routes ----------
@app.get("/api/status")
def status():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    # чтобы при открытии домена сразу открывался мини-апп
    return RedirectResponse(url="/webapp/")


@app.get("/webapp/", include_in_schema=False)
def webapp_index():
    index_path = WEBAPP_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h3>webapp/index.html not found</h3>", status_code=404)
    return FileResponse(index_path)


@app.get("/api/listings")
def get_listings(
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None, alias="type"),
    max_price: Optional[float] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    items = load_listings()

    city_n = norm(city).lower()
    district_n = norm(district).lower()
    type_n = norm(type).lower()

    def match(item: Dict[str, Any]) -> bool:
        if city_n:
            if norm(item.get("city")).lower() != city_n:
                return False
        if district_n:
            if norm(item.get("district")).lower() != district_n:
                return False
        if type_n:
            if norm(item.get("type")).lower() != type_n:
                return False
        if max_price is not None:
            try:
                price = float(item.get("price", 0))
            except Exception:
                price = 0.0
            if price > float(max_price):
                return False
        return True

    filtered = [x for x in items if match(x)]
    return filtered[:limit]


@app.get("/api/filters")
def get_filters():
    items = load_listings()
    cities = uniq_sorted([str(x.get("city", "")).strip() for x in items])
    districts = uniq_sorted([str(x.get("district", "")).strip() for x in items])
    types = uniq_sorted([str(x.get("type", "")).strip() for x in items])

    return {
        "cities": cities,
        "districts": districts,
        "types": types,
    }
