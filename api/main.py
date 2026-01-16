from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp"
DATA_PATH = BASE_DIR / "data" / "listings.json"

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для Telegram Mini App ок
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_listings() -> list[dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # ожидаем список объектов
    return data if isinstance(data, list) else []


def normalize(s: Any) -> str:
    return str(s).strip()


@app.get("/api/status")
def status():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    # чтобы при открытии домена сразу открывался миниапп
    return RedirectResponse(url="/webapp/")


# Статика миниаппа
if WEBAPP_DIR.exists():
    app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")


@app.get("/webapp/", include_in_schema=False)
def webapp_index():
    index_path = WEBAPP_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h3>webapp/index.html not found</h3>", status_code=404)
    return FileResponse(index_path)


@app.get("/api/filters")
def get_filters():
    listings = load_listings()

    cities = sorted({normalize(x.get("city")) for x in listings if normalize(x.get("city"))})
    districts = sorted({normalize(x.get("district")) for x in listings if normalize(x.get("district"))})
    types = sorted({normalize(x.get("type")) for x in listings if normalize(x.get("type"))})

    return {"cities": cities, "districts": districts, "types": types}


@app.get("/api/listings")
def get_listings(
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None, alias="type"),
    max_price: Optional[float] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    listings = load_listings()

    if city:
        city_n = normalize(city).lower()
        listings = [x for x in listings if normalize(x.get("city")).lower() == city_n]

    if district:
        district_n = normalize(district).lower()
        listings = [x for x in listings if normalize(x.get("district")).lower() == district_n]

    if type:
        type_n = normalize(type).lower()
        listings = [x for x in listings if normalize(x.get("type")).lower() == type_n]

    if max_price is not None:
        try:
            mp = float(max_price)
            listings = [x for x in listings if float(x.get("price", 0) or 0) <= mp]
        except Exception:
            pass

    return listings[:limit]
