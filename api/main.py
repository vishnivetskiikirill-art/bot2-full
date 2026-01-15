from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
WEBAPP_DIR = BASE_DIR / "webapp"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LISTINGS_PATH = DATA_DIR / "listings.json"   # <-- ВАЖНО: должен быть listings.json (не .txt)


# ---------------- App ----------------
app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздаём статику миниаппа
# /webapp/styles.css, /webapp/app.js, /webapp/index.html
if WEBAPP_DIR.exists():
    app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")


# ---------------- Helpers ----------------
def load_listings() -> List[Dict[str, Any]]:
    if not LISTINGS_PATH.exists():
        return []
    try:
        return json.loads(LISTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def normalize_str(x: Any) -> str:
    return str(x).strip() if x is not None else ""


# ---------------- Routes ----------------
@app.get("/api/status")
def status():
    return {"status": "ok"}


# чтобы при открытии домена не видеть {"status":"ok"},
# а сразу открывался миниапп
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
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None, alias="ptype"),
    max_price: Optional[int] = Query(default=None),
):
    items = load_listings()

    city_n = normalize_str(city).lower() if city else None
    district_n = normalize_str(district).lower() if district else None
    type_n = normalize_str(type).lower() if type else None

    out: List[Dict[str, Any]] = []
    for it in items:
        it_city = normalize_str(it.get("city")).lower()
        it_district = normalize_str(it.get("district")).lower()
        it_type = normalize_str(it.get("type")).lower()

        price_val = it.get("price")
        try:
            price_int = int(price_val) if price_val is not None else None
        except Exception:
            price_int = None

        if city_n and it_city != city_n:
            continue
        if district_n and it_district != district_n:
            continue
        if type_n and it_type != type_n:
            continue
        if max_price is not None and price_int is not None and price_int > max_price:
            continue

        out.append(it)

    return out


@app.get("/api/filters")
def get_filters():
    items = load_listings()
    cities = sorted({normalize_str(i.get("city")) for i in items if normalize_str(i.get("city"))})
    districts = sorted({normalize_str(i.get("district")) for i in items if normalize_str(i.get("district"))})
    types = sorted({normalize_str(i.get("type")) for i in items if normalize_str(i.get("type"))})

    return {
        "cities": cities,
        "districts": districts,
        "types": types,
    }
