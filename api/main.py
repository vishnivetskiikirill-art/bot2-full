from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent          # .../api
WEBAPP_DIR = BASE_DIR / "webapp"                   # .../api/webapp
DATA_FILE = BASE_DIR / "data" / "listings.json"    # .../api/data/listings.json

# 1) Статика: /static/app.js, /static/style.css и т.п.
app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR)), name="static")


def load_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def index():
    # 2) Главная страница — ТОЛЬКО index.html
    return FileResponse(WEBAPP_DIR / "index.html")


@app.get("/api/status")
def status():
    return {"status": "ok"}


@app.get("/api/listings")
def get_listings(
    city: str | None = None,
    district: str | None = None,
    type: str | None = Query(default=None, alias="type"),
    max_price: int | None = None,
):
    items = load_listings()

    def ok(x):
        if city and x.get("city") != city:
            return False
        if district and x.get("district") != district:
            return False
        if type and x.get("type") != type:
            return False
        if max_price is not None and int(x.get("price", 0)) > max_price:
            return False
        return True

    return [x for x in items if ok(x)]


@app.get("/api/meta")
def get_meta():
    items = load_listings()
    cities = sorted({x.get("city") for x in items if x.get("city")})
    districts = sorted({x.get("district") for x in items if x.get("district")})
    types = sorted({x.get("type") for x in items if x.get("type")})
    return {"cities": cities, "districts": districts, "types": types}
