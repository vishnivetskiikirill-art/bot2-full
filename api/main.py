import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp"
DATA_FILE = BASE_DIR / "data" / "listings.json"

app = FastAPI()

# Статика (js/css/картинки)
app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR / "static")), name="static")


def load_listings() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


@app.get("/api/status")
def status():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    return (WEBAPP_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/detail", response_class=HTMLResponse)
def detail_page():
    return (WEBAPP_DIR / "detail.html").read_text(encoding="utf-8")


@app.get("/api/listings")
def get_listings(
    city: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    max_price: Optional[int] = Query(default=None),
):
    items = load_listings()

    def ok(x: Dict[str, Any]) -> bool:
        if city and x.get("city") != city:
            return False
        if district and x.get("district") != district:
            return False
        if type and x.get("type") != type:
            return False
        if max_price is not None and int(x.get("price", 0)) > int(max_price):
            return False
        return True

    return [x for x in items if ok(x)]


@app.get("/api/filters")
def get_filters():
    items = load_listings()
    cities = sorted({x.get("city") for x in items if x.get("city")})
    districts = sorted({x.get("district") for x in items if x.get("district")})
    types = sorted({x.get("type") for x in items if x.get("type")})
    return {"cities": cities, "districts": districts, "types": types}


@app.get("/api/listings/{listing_id}")
def get_listing_by_id(listing_id: int):
    items = load_listings()
    for x in items:
        if int(x.get("id", 0)) == listing_id:
            return x
    return JSONResponse({"detail": "Not Found"}, status_code=404)
