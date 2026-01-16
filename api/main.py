from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp"
STATIC_DIR = WEBAPP_DIR / "static"
DATA_FILE = BASE_DIR / "data" / "listings.json"

# папка static обязана существовать
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def load_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []

    # гарантируем id (если его нет в listings.json)
    for i, item in enumerate(data):
        if isinstance(item, dict) and "id" not in item:
            item["id"] = i + 1
    return data


@app.get("/")
def index():
    return FileResponse(str(WEBAPP_DIR / "index.html"))


@app.get("/detail.html")
def detail_page():
    return FileResponse(str(WEBAPP_DIR / "detail.html"))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filters():
    items = load_listings()

    cities = sorted({x.get("city") for x in items if x.get("city")})
    districts = sorted({x.get("district") for x in items if x.get("district")})
    types = sorted({x.get("type") for x in items if x.get("type")})

    return {"cities": cities, "districts": districts, "types": types}


@app.get("/api/listings")
def listings(
    city: str | None = None,
    district: str | None = None,
    type: str | None = None,
    max_price: int | None = Query(default=None, ge=0),
):
    items = load_listings()

    def ok(x: dict) -> bool:
        if city and x.get("city") != city:
            return False
        if district and x.get("district") != district:
            return False
        if type and x.get("type") != type:
            return False
        if max_price is not None:
            price = int(x.get("price") or 0)
            if price > max_price:
                return False
        return True

    return [x for x in items if ok(x)]


@app.get("/api/listings/{listing_id}")
def listing_detail(listing_id: int):
    items = load_listings()
    for x in items:
        try:
            if int(x.get("id")) == listing_id:
                return x
        except Exception:
            continue
    raise HTTPException(status_code=404, detail="Listing not found")
